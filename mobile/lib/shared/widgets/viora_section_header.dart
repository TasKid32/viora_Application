import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_styles.dart';

/// Consistent section header with icon + title.
///
/// Replaces the various inline section title patterns across screens.
class VioraSectionHeader extends StatelessWidget {
  final String title;
  final IconData icon;
  final Color? color;
  final Widget? trailing;

  const VioraSectionHeader({
    super.key,
    required this.title,
    required this.icon,
    this.color,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    final c = color ?? AppColors.primary;
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: c.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(AppRadius.sm),
            ),
            child: Icon(icon, color: c, size: 18),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(title, style: AppTextStyles.h4),
          ),
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}
