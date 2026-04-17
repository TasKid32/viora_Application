import 'package:flutter/material.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../../../shared/widgets/viora_card.dart';
import '../../../shared/widgets/viora_empty_state.dart';
import '../provider/notification_provider.dart';

/// Notifications screen.
class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});
  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => context.read<NotificationProvider>().load());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: 
        Text(AppLocalizations.of(context)!.notifications),

 actions: [
          // Mark all as read button
          Consumer<NotificationProvider>(
            builder: (context, provider, _) {
              if (provider.unreadCount > 0) {
                return IconButton(
                  icon: const Icon(Icons.done_all),
                  tooltip: 'Mark all as read',
                  onPressed: () async {
                    try {
                      await provider.markAllAsRead();
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('All notifications marked as read'),
                            duration: Duration(seconds: 2),
                          ),
                        );
                      }
                    } catch (e) {
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Failed to mark all as read: $e'),
                            backgroundColor: AppColors.error,
                          ),
                        );
                      }
                    }
                  },
                );
              }
              return const SizedBox.shrink();
            },
          ),
        ],

      ),
      body: Selector<NotificationProvider, bool>(
        selector: (_, p) => p.loading,
        builder: (_, loading, __) {
          if (loading) {
            return const Center(
                child: CircularProgressIndicator(color: AppColors.primary));
          }

          final provider = context.watch<NotificationProvider>();

          if (provider.error != null) {
            return VioraEmptyState(
              icon: Icons.error_outline,
              title: provider.error!,
              actionLabel: AppLocalizations.of(context)!.retry,
              onAction: () => provider.load(),
            );
          }

          if (provider.notifications.isEmpty) {
            return VioraEmptyState(
              icon: Icons.notifications_none,
              title: AppLocalizations.of(context)!.noNotificationsYet,
              subtitle: AppLocalizations.of(context)!.notificationsEmptyDesc,
            );
          }

          return RefreshIndicator(
            onRefresh: () => provider.load(),
            color: AppColors.primary,
            child: ListView.builder(
              padding: AppSpacing.screenPadding,
              itemCount: provider.notifications.length,
              itemBuilder: (_, i) =>
                  _NotificationTile(notification: provider.notifications[i]),
            ),
          );
        },
      ),
    );
  }
}

class _NotificationTile extends StatelessWidget {
  final AppNotification notification;
  const _NotificationTile({required this.notification});

  @override
  Widget build(BuildContext context) {
    return VioraCard(
      color: notification.isRead ? null : AppColors.surfaceTinted,
      borderColor: notification.isRead
          ? null
          : AppColors.primary.withValues(alpha: 0.15),
      margin: const EdgeInsets.only(bottom: 8),
      padding: EdgeInsets.zero,
      onTap: () {
        if (!notification.isRead) {
          context.read<NotificationProvider>().markAsRead(notification.id);
        }
      },
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Icon container
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: notification.color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(AppRadius.sm),
              ),
              child:
                  Icon(notification.icon, color: notification.color, size: 20),
            ),
            const SizedBox(width: 12),
            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    notification.title,
                    style: AppTextStyles.bodyBold.copyWith(
                      fontWeight: notification.isRead
                          ? FontWeight.w400
                          : FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    notification.message,
                    style: AppTextStyles.bodySmall
                        .copyWith(color: AppColors.textSecondary),
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 6),
                  Text(
                    _timeAgo(
                        notification.createdAt, AppLocalizations.of(context)!),
                    style: AppTextStyles.caption
                        .copyWith(color: AppColors.textHint),
                  ),
                ],
              ),
            ),
            // Unread dot
            if (!notification.isRead)
              Container(
                width: 8,
                height: 8,
                margin: const EdgeInsets.only(top: 6),
                decoration: const BoxDecoration(
                  color: AppColors.primary,
                  shape: BoxShape.circle,
                ),
              ),
          ],
        ),
      ),
    );
  }

  String _timeAgo(DateTime dt, AppLocalizations l10n) {
    final diff = DateTime.now().difference(dt);
    if (diff.inMinutes < 1) return l10n.justNow;
    if (diff.inMinutes < 60) return l10n.minutesAgo(diff.inMinutes);
    if (diff.inHours < 24) return l10n.hoursAgo(diff.inHours);
    if (diff.inDays < 2) return l10n.yesterday;
    if (diff.inDays < 7) return l10n.daysAgo(diff.inDays);
    return '${dt.day}/${dt.month}/${dt.year}';
  }
}
