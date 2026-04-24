import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';


/// Notification response wrapper with unread count.
class NotificationResponse {
  final int unreadCount;
  final List<AppNotification> notifications;

  const NotificationResponse({
    required this.unreadCount,
    required this.notifications,
  });

  factory NotificationResponse.fromJson(Map<String, dynamic> json) {
    final list = json['notifications'] as List? ?? [];
    return NotificationResponse(
      unreadCount: json['unread_count'] as int? ?? 0,
      notifications: list.map((n) => AppNotification.fromJson(n as Map<String, dynamic>)).toList(),
    );
  }
}

/// Notification model with i18n support.
///
/// [titleKey]/[messageKey] are translation keys for client-side localization.
/// [data] contains template variables for string interpolation.
/// [title]/[message] are English fallbacks from the server.

class AppNotification {
  final String id;
  final String title;
  final String message;
  final String type;
  final bool isRead;
  final DateTime createdAt;

 // ── i18n fields ──────────────────────────────────────────
  final String? titleKey;
  final String? messageKey;
  final Map<String, dynamic>? data;


  const AppNotification({
    required this.id,
    required this.title,
    required this.message,
    required this.type,
    this.isRead = false,
    required this.createdAt,
    this.titleKey,
    this.messageKey,
    this.data,
  });

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id']?.toString() ?? '',
      title: json['title'] as String? ?? '',
      message: json['message'] as String? ?? '',
      type: json['type'] as String? ?? 'general',
      isRead: json['is_read'] as bool? ?? false,
      createdAt: DateTime.tryParse(json['timestamp'] ?? json['created_at'] ?? '') ?? DateTime.now(),
       titleKey: json['title_key'] as String?,
      messageKey: json['message_key'] as String?,
      data: json['data'] is Map ? Map<String, dynamic>.from(json['data']) : null,
    );
  }

  /// Create a copy with updated fields.
  AppNotification copyWith({
    String? id,
    String? title,
    String? message,
    String? type,
    bool? isRead,
    DateTime? createdAt,
     String? titleKey,
    String? messageKey,
    Map<String, dynamic>? data,
  }) {
    return AppNotification(
      id: id ?? this.id,
      title: title ?? this.title,
      message: message ?? this.message,
      type: type ?? this.type,
      isRead: isRead ?? this.isRead,
      createdAt: createdAt ?? this.createdAt,
      titleKey: titleKey ?? this.titleKey,
      messageKey: messageKey ?? this.messageKey,
      data: data ?? this.data,
    );
  }

  IconData get icon {
    switch (type) {
      case 'cv_analysis': return Icons.analytics_outlined;
      case 'roadmap': return Icons.route_outlined;
      case 'course': return Icons.school_outlined;
      case 'achievement': return Icons.emoji_events_outlined;
      case 'system': return Icons.info_outline;
      default: return Icons.notifications_outlined;
    }
  }

  Color get color {
    switch (type) {
       case 'cv_analysis': return AppColors.info;
      case 'roadmap': return AppColors.primary;
      case 'course': return AppColors.success;
      case 'achievement': return AppColors.warning;
       case 'system': return AppColors.textSecondary;
      default: return AppColors.textSecondary;
    }
  }
}
