import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import '../../../core/utils/logger.dart';
import '../../../core/utils/error_helper.dart';
import '../data/notification_api.dart';
import '../data/notification_models.dart';

/// Re-export model so screens can import from one place.
export '../data/notification_models.dart';

/// Notification provider — manages notification state.
class NotificationProvider extends ChangeNotifier {
  final NotificationApi _api;
  NotificationProvider({required NotificationApi api}) : _api = api;

  List<AppNotification> _notifications = [];
  bool _loading = false;
  String? _error;

  List<AppNotification> get notifications => _notifications;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> load() async {
    _loading = true;
    _error = null;
    notifyListeners();

    try {
      _notifications = await _api.getNotifications();
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        _notifications = [];
      } else {
        _error = extractDioError(e);
        Log.e('Notifications', 'Load failed', e.message);
      }
    } catch (e) {
      _error = 'An unexpected error occurred';
      Log.e('Notifications', 'Unexpected', e);
    }

    _loading = false;
    notifyListeners();
  }

  Future<void> markAsRead(String id) async {
    try {
      await _api.markAsRead(id);
      final idx = _notifications.indexWhere((n) => n.id == id);
      if (idx >= 0) {
        _notifications[idx] = _notifications[idx].copyWith(isRead: true);
        notifyListeners();
      }
    } catch (e) {
      Log.e('Notifications', 'Mark read failed', e);
    }
  }
}
