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
  int _unreadCount = 0;
  bool _loading = false;
  String? _error;

  List<AppNotification> get notifications => _notifications;
  int get unreadCount => _unreadCount;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> load() async {
    _loading = true;
    _error = null;
    notifyListeners();

    try {
       final response = await _api.getNotifications();
      _notifications = response.notifications;
      _unreadCount = response.unreadCount;
    } 
    on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        _notifications = [];
        _unreadCount = 0;
      } 
      else {
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
      if (idx >= 0 && !_notifications[idx].isRead) {
        _notifications[idx] = 
        _notifications[idx].copyWith(isRead: true);
        _unreadCount = 
        (_unreadCount - 1).clamp(0, _notifications.length);
      
        notifyListeners();
      }
    } catch (e) {
      Log.e('Notifications', 'Mark read failed', e);
    }
  }
Future<void> markAllAsRead() async {
    try {
      await _api.markAllAsRead();
      _notifications = _notifications.map((n) => n.copyWith(isRead: true)).toList();
      _unreadCount = 0;
      notifyListeners();
    } catch (e) {
      Log.e('Notifications', 'Mark all read failed', e);
      rethrow;
    }
  }

  Future<void> deleteNotification(String id) async {
    try {
      await _api.deleteNotification(id);
      final wasUnread = _notifications.firstWhere((n) => n.id == id, orElse: () => _notifications.first).isRead == false;
      _notifications.removeWhere((n) => n.id == id);
      if (wasUnread) {
        _unreadCount = (_unreadCount - 1).clamp(0, _notifications.length);
      }
      notifyListeners();
    } catch (e) {
      Log.e('Notifications', 'Delete failed', e);
      rethrow;
    }
  }

}
