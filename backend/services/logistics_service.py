from datetime import datetime
from backend.extensions import db
from backend.models.order import Order
from backend.models.logistics_company import LogisticsCompany
try:
    from aftership import APIv4
except ImportError:
    APIv4 = None
from flask import current_app
import logging
from celery import shared_task
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

logger = logging.getLogger(__name__)

@shared_task
def update_tracking_status(order_id):
    """
    Celery 任務：異步更新訂單的物流狀態
    """
    service = LogisticsService()
    try:
        order = Order.query.get(order_id)
        if order and order.tracking_number and order.logistics_company_id:
            company = LogisticsCompany.query.get(order.logistics_company_id)
            tracking_info = service.track_shipment(order.tracking_number, company.aftership_slug)
            if tracking_info:
                service._update_order_status(order, tracking_info)
    except Exception as e:
        logger.error(f'Failed to update tracking status for order {order_id}: {str(e)}')

class LogisticsService:
    def __init__(self, api_key=None):
        # 支援外部傳入 api_key，否則於有 app context 時才存取 current_app
        if api_key is not None:
            self.api_key = api_key
        else:
            try:
                self.api_key = current_app.config.get('AFTERSHIP_API_KEY')
            except RuntimeError:
                self.api_key = None
        
        if self.api_key:
            self.api = APIv4(self.api_key) if APIv4 else None
        else:
            self.api = None
            logger.warning('AfterShip API key not configured')
        
        self.geolocator = Nominatim(user_agent="group-buy-platform")

    def _get_coordinates(self, location):
        """
        將地址轉換為經緯度坐標
        """
        try:
            if not location:
                return None
            location_data = self.geolocator.geocode(location)
            if location_data:
                return {
                    'lat': location_data.latitude,
                    'lng': location_data.longitude
                }
        except GeocoderTimedOut:
            logger.warning(f'Geocoding timed out for location: {location}')
        except Exception as e:
            logger.error(f'Failed to geocode location {location}: {str(e)}')
        return None

    def _update_order_status(self, order, tracking):
        """
        根據追蹤資訊更新訂單狀態
        """
        try:
            tag = tracking.get('tag')
            if tag == 'Delivered':
                order.status = 'completed'
                order.received_at = datetime.now()
            elif tag in ['InTransit', 'OutForDelivery']:
                order.status = 'shipped'
            
            db.session.commit()
        except Exception as e:
            logger.error(f'Failed to update order status: {str(e)}')
            db.session.rollback()

    def get_tracking_info(self, order_id, user_id):
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")
        if order.user_id != user_id:
            raise ValueError("Order does not belong to user")
        
        if not order.tracking_number or not order.logistics_company_id:
            raise ValueError("No tracking information available")

        company = LogisticsCompany.query.get(order.logistics_company_id)
        if not company:
            raise ValueError("Logistics company not found")

        # 如果配置了 AfterShip API，使用真實的追蹤資訊
        if self.api and company.aftership_slug:
            try:
                tracking = self.track_shipment(order.tracking_number, company.aftership_slug)
                if tracking:
                    return self._convert_aftership_to_response(tracking, order, company)
            except Exception as e:
                logger.error(f'Failed to get tracking from AfterShip: {str(e)}')
                # 如果 API 調用失敗，返回模擬數據

        # 返回模擬數據
        return self._get_mock_tracking_info(order, company)
        
    def track_shipment(self, tracking_number, courier=None):
        """
        使用 AfterShip API 追蹤物流狀態
        """
        if not self.api:
            return None
            
        try:
            if not courier:
                try:
                    result = self.api.couriers.detect(tracking_number)
                    if result and hasattr(result, 'couriers') and result.couriers:
                        courier = result.couriers[0].slug
                except Exception as e:
                    logger.warning(f'Failed to detect courier for tracking number {tracking_number}: {str(e)}')
            
            if not courier:
                raise ValueError('Unable to detect courier')
            
            tracking = self.api.trackings.get(tracking_number, courier)
            if tracking and hasattr(tracking, 'tracking'):
                return tracking.tracking
            return None
            
        except Exception as e:
            logger.error(f'Failed to track shipment {tracking_number}: {str(e)}')
            return None

    def _convert_aftership_to_response(self, tracking, order, company):
        """將 AfterShip 的回應轉換為標準格式"""
        history = []
        current_status = tracking.get('tag', order.status)
        current_location = tracking.get('location')
        route_coordinates = []

        # 添加訂單建立記錄
        history.append({
            "status": "訂單建立",
            "location": "系統",
            "timestamp": order.created_at.isoformat(),
            "description": "訂單已成功建立",
            "coordinates": None
        })

        # 添加付款記錄
        if order.status in ['paid', 'shipped', 'completed']:
            history.append({
                "status": "已付款",
                "location": "系統",
                "timestamp": order.payment_deadline.isoformat(),
                "description": "訂單已完成付款",
                "coordinates": None
            })

        # 添加 AfterShip 的追蹤記錄
        checkpoints = tracking.get('checkpoints', [])
        for checkpoint in checkpoints:
            location = checkpoint.get('location', '未知')
            coordinates = self._get_coordinates(location)
            if coordinates:
                route_coordinates.append(coordinates)
            
            history.append({
                "status": checkpoint.get('tag', '運送中'),
                "location": location,
                "timestamp": checkpoint.get('checkpoint_time'),
                "description": checkpoint.get('message', ''),
                "coordinates": coordinates
            })

        return {
            "order_id": order.id,
            "tracking_number": order.tracking_number,
            "logistics_company": company.name,
            "current_status": current_status,
            "current_location": current_location,
            "expected_delivery": tracking.get('expected_delivery'),
            "history": history,
            "route": route_coordinates
        }

    def _get_mock_tracking_info(self, order, company):
        """獲取模擬的物流追蹤信息"""
        tracking_history = [
            {
                "status": "訂單建立",
                "location": "系統",
                "timestamp": order.created_at.isoformat(),
                "description": "訂單已成功建立"
            }
        ]

        if order.status in ['paid', 'shipped', 'completed']:
            tracking_history.append({
                "status": "已付款",
                "location": "系統",
                "timestamp": order.payment_deadline.isoformat(),
                "description": "訂單已完成付款"
            })

        if order.status in ['shipped', 'completed']:
            tracking_history.append({
                "status": "已出貨",
                "location": company.name,
                "timestamp": order.shipped_at.isoformat(),
                "description": f"包裹已由{company.name}收件"
            })

        if order.status == 'completed':
            tracking_history.append({
                "status": "已送達",
                "location": order.recipient_address,
                "timestamp": order.received_at.isoformat(),
                "description": "包裹已送達收件地址"
            })

        return {
            "order_id": order.id,
            "tracking_number": order.tracking_number,
            "logistics_company": company.name,
            "current_status": order.status,
            "history": tracking_history
        }