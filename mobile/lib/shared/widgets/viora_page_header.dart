import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_styles.dart';

/// Unified page header for content sections within screens.
///
/// Use when a screen needs a prominent title + optional subtitle
/// inside the scrollable body (not in the AppBar).
///
/// The title defines the task/section.
/// The subtitle explains the action benefit — never repeats the title.
///
/// Usage:
/// ```dart
/// VioraPageHeader(
///   title: 'Upload Your CV',
///   subtitle: 'We'll extract skills and match you with careers',
///   icon: Icons.cloud_upload_outlined,
/// )
/// ```
class VioraPageHeader extends StatelessWidget {
  final String title;
  final String? subtitle;
  final IconData? icon;
  final Widget? trailing;

  const VioraPageHeader({
    super.key,
    required this.title,
    this.subtitle,
    this.icon,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Optional leading icon
          if (icon != null) ...[
            Container(
              width: 40, height: 40,
              margin: const EdgeInsets.only(top: 2),
              decoration: BoxDecoration(
                color: AppColors.primaryContainer,
                borderRadius: BorderRadius.circular(AppRadius.sm),
              ),
              child: Icon(icon, color: AppColors.primary, size: 20),
            ),
            const SizedBox(width: 12),
          ],
          // Title + subtitle
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: AppTextStyles.h2.copyWith(color: AppColors.primary)),
                if (subtitle != null && subtitle!.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    subtitle!,
                    style: AppTextStyles.body.copyWith(color: AppColors.textSecondary, height: 1.4),
                  ),
                ],
              ],
            ),
          ),
          // Optional trailing widget
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}
