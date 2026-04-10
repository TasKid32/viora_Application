import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import 'notification_models.dart';

/// Notifications API — thin wrapper around ApiClient.
class NotificationApi {
  final ApiClient _api;
  NotificationApi(this._api);

  /// Load all notifications.
  Future<List<AppNotification>> getNotifications() async {
    final response = await _api.get(Endpoints.notifications);
    final list = response.data['notifications'] as List? ?? [];
    return list.map((n) => AppNotification.fromJson(n as Map<String, dynamic>)).toList();
  }

  /// Mark a notification as read.
  Future<void> markAsRead(String id) async {
    await _api.put(Endpoints.notificationRead(id));
  }
}
