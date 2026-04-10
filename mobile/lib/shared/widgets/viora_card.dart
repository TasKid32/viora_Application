import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_styles.dart';

/// Unified card wrapper used across all screens.
///
/// Provides consistent border radius, padding, and optional tap behavior.
/// Usage:
/// ```dart
/// VioraCard(
///   child: Text('Hello'),
///   onTap: () => print('tapped'),
/// )
/// ```
class VioraCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final Color? color;
  final Color? borderColor;
  final VoidCallback? onTap;
  final double? borderRadius;

  const VioraCard({
    super.key,
    required this.child,
    this.padding,
    this.margin,
    this.color,
    this.borderColor,
    this.onTap,
    this.borderRadius,
  });

  @override
  Widget build(BuildContext context) {
    final radius = BorderRadius.circular(borderRadius ?? AppRadius.lg);

    Widget content = Container(
      width: double.infinity,
      padding: padding ?? AppSpacing.cardPadding,
      margin: margin,
      decoration: BoxDecoration(
        color: color ?? AppColors.surface,
        borderRadius: radius,
        border: Border.all(
          color: borderColor ?? AppColors.outlineVariant,
          width: 1,
        ),
        boxShadow: AppShadows.sm,
      ),
      child: child,
    );

    if (onTap != null) {
      content = InkWell(
        onTap: onTap,
        borderRadius: radius,
        child: content,
      );
    }

    return content;
  }
}

/// Emphasized card with colored background — for progress / hero sections.
///
/// Uses a soft container color instead of heavy gradients.
class VioraHighlightCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final Color? backgroundColor;

  const VioraHighlightCard({
    super.key,
    required this.child,
    this.padding,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: padding ?? AppSpacing.cardPadding,
      decoration: BoxDecoration(
        color: backgroundColor ?? AppColors.primaryContainer,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        boxShadow: AppShadows.sm,
      ),
      child: child,
    );
  }
}
