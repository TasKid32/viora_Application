import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import 'notification_models.dart';

/// Notifications API — thin wrapper around ApiClient.
class NotificationApi {
  final ApiClient _api;
  NotificationApi(this._api);

  /// Load all notifications with unread count.
  Future<NotificationResponse> getNotifications() async {
    final response = await _api.get(Endpoints.notifications);
    return NotificationResponse.fromJson(response.data);
  }

  /// Mark a notification as read.
  Future<void> markAsRead(String id) async {
    await _api.put(Endpoints.notificationRead(id));
  }

/// Mark all notifications as read.
  Future<void> markAllAsRead() async {
    await _api.put(Endpoints.notificationReadAll);
  }

  /// Delete a notification.
  Future<void> deleteNotification(String id) async {
    await _api.delete(Endpoints.notificationDelete(id));
  }


}
