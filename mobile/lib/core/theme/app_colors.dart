import 'package:flutter/material.dart';

/// Viora design system colors — single source of truth.
///
/// Aligned with Material 3 color roles where possible.
/// Use [AppColors.colorScheme] in ThemeData for full M3 integration.
class AppColors {
  AppColors._();

  // ─── Brand ──────────────────────────────────────────
  static const Color primary = Color(0xFF7C3AED);
  static const Color primaryLight = Color(0xFFA78BFA);
  static const Color primaryMuted = Color(0xFFB197FC); // softer accent for badges
  static const Color accent = Color(0xFFEC4899);

  // ─── M3 Surface / Container roles ──────────────────
  static const Color primaryContainer = Color(0xFFEDE9FE);
  static const Color onPrimaryContainer = Color(0xFF4C1D95);
  static const Color primarySurface = Color(0xFFF5F3FF);   // very subtle tint
  static const Color surfaceTinted = Color(0xFFFAF8FF);    // barely-there brand tint for cards

  // ─── Semantic ───────────────────────────────────────
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFEAB308);
  static const Color error = Color(0xFFEF4444);
  static const Color info = Color(0xFF3B82F6);

  // ─── Neutrals ───────────────────────────────────────
  static const Color white = Color(0xFFFFFFFF);
  static const Color background = Color(0xFFF9F8FC);      // near-white with subtle purple warmth
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceVariant = Color(0xFFF1F3F5);
  static const Color textPrimary = Color(0xFF1A1C1E);
  static const Color textSecondary = Color(0xFF6B7280);
  static const Color textHint = Color(0xFF9CA3AF);
  static const Color border = Color(0xFFE5E7EB);
  static const Color outline = Color(0xFFE0E0E0);
  static const Color outlineVariant = Color(0xFFEEEEEE);
  static const Color divider = Color(0xFFF3F4F6);

  // ─── Gradients ─────────────────────────────────────
  /// Full brand gradient — splash screen, loading, chat header.
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primary, accent],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  /// Soft hero gradient — progress cards, hero sections only.
  /// Deliberate and subtle: deep purple → lighter purple.
  static const LinearGradient heroGradient = LinearGradient(
    colors: [Color(0xFF7C3AED), Color(0xFF9F67FF)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
