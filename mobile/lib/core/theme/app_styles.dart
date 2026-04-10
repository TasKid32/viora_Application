import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

/// Text styles used throughout the app.
///
/// Uses Google Fonts (Inter) for modern, clean typography.
class AppTextStyles {
  AppTextStyles._();

  static final String? _fontFamily = GoogleFonts.inter().fontFamily;

  // ─── Headers ────────────────────────────────────────
  static TextStyle h1 = TextStyle(
    fontSize: 28, fontWeight: FontWeight.bold, color: AppColors.textPrimary, fontFamily: _fontFamily,
  );
  static TextStyle h2 = TextStyle(
    fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.textPrimary, fontFamily: _fontFamily,
  );
  static TextStyle h3 = TextStyle(
    fontSize: 18, fontWeight: FontWeight.w600, color: AppColors.textPrimary, fontFamily: _fontFamily,
  );
  static TextStyle h4 = TextStyle(
    fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary, fontFamily: _fontFamily,
  );

  // ─── Body ───────────────────────────────────────────
  static TextStyle bodyLarge = TextStyle(
    fontSize: 16, fontWeight: FontWeight.w400, color: AppColors.textPrimary, fontFamily: _fontFamily,
  );
  static TextStyle body = TextStyle(
    fontSize: 14, fontWeight: FontWeight.w400, color: AppColors.textPrimary, fontFamily: _fontFamily,
  );
  static TextStyle bodySmall = TextStyle(
    fontSize: 12, fontWeight: FontWeight.w400, color: AppColors.textSecondary, fontFamily: _fontFamily,
  );

  // ─── Bold variants ─────────────────────────────────
  static TextStyle bodyBold = TextStyle(
    fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary, fontFamily: _fontFamily,
  );
  static TextStyle bodySmallBold = TextStyle(
    fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textSecondary, fontFamily: _fontFamily,
  );

  // ─── Special ────────────────────────────────────────
  static TextStyle button = TextStyle(
    fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.white, fontFamily: _fontFamily,
  );
  static TextStyle caption = TextStyle(
    fontSize: 12, fontWeight: FontWeight.w400, color: AppColors.textHint, fontFamily: _fontFamily,
  );
  static TextStyle label = TextStyle(
    fontSize: 14, fontWeight: FontWeight.w500, color: AppColors.textSecondary, fontFamily: _fontFamily,
  );
}

/// Spacing constants — 4px base grid.
class AppSpacing {
  AppSpacing._();

  static const double xs = 4;
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 24;
  static const double xxl = 32;

  /// Gap between major sections (e.g. between cards).
  static const double sectionGap = 24;

  /// Gap between related items within a section.
  static const double itemGap = 12;

  /// Bottom padding to clear FAB on scrollable screens.
  static const double fabClearance = 88;

  static const EdgeInsets screenPadding = EdgeInsets.symmetric(horizontal: 20, vertical: 16);
  static const EdgeInsets cardPadding = EdgeInsets.all(20);
}

/// Border radius constants.
class AppRadius {
  AppRadius._();

  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 20;
  static const double full = 100;
}

/// Unified shadow / elevation tokens.
///
/// Use these instead of defining BoxShadow inline in every widget.
class AppShadows {
  AppShadows._();

  /// No shadow — flat surfaces.
  static const List<BoxShadow> none = [];

  /// Subtle shadow for cards.
  static const List<BoxShadow> sm = [
    BoxShadow(
      color: Color(0x0A000000), // black @ 4%
      blurRadius: 8,
      offset: Offset(0, 2),
    ),
  ];

  /// Medium shadow for floating elements (FAB, bottom sheets, modals).
  static const List<BoxShadow> md = [
    BoxShadow(
      color: Color(0x0F000000), // black @ 6%
      blurRadius: 16,
      offset: Offset(0, 4),
    ),
  ];

  /// Elevation for top-level overlays.
  static const List<BoxShadow> lg = [
    BoxShadow(
      color: Color(0x14000000), // black @ 8%
      blurRadius: 24,
      offset: Offset(0, 8),
    ),
  ];
}
