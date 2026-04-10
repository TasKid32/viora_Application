import 'package:dio/dio.dart';
import 'package:viora_app/l10n/app_localizations.dart';

/// Shared error extraction — DRY helper used by all providers.
///
/// Extracts Backend's actual error message from DioException response.
/// When [l10n] is provided, translates known error patterns to localized messages.
/// Falls back to English when no Backend response exists.
String extractDioError(DioException e, {AppLocalizations? l10n}) {
  // Use Backend's detail message directly
  final data = e.response?.data;
  if (data is Map && data.containsKey('detail')) {
    final detail = data['detail'] as String;

    // When localization is available, translate known error patterns
    if (l10n != null) {
      final translated = _translateKnownError(detail, l10n);
      if (translated != null) return translated;
    }

    return detail; // Fallback: show raw Backend message
  }

  // Status-code based messages
  final statusCode = e.response?.statusCode;
  if (l10n != null && statusCode != null) {
    if (statusCode == 429) return l10n.errorQuotaExceeded;
    if (statusCode == 413) return l10n.errorFileTooLarge;
  }

  // Network-level errors
  if (e.type == DioExceptionType.connectionTimeout) {
    return l10n?.errorConnectionTimeout ??
        'Connection timed out — check your network';
  }
  if (e.type == DioExceptionType.connectionError) {
    return l10n?.errorNoConnection ?? 'Could not connect to server';
  }
  if (e.type == DioExceptionType.receiveTimeout) {
    return l10n?.errorAnalysisTimeout ??
        'Analysis took too long — please try again';
  }

  return l10n?.errorGeneric ?? 'An error occurred — please try again';
}

/// Maps known backend error detail strings to localized messages.
String? _translateKnownError(String detail, AppLocalizations l10n) {
  final lower = detail.toLowerCase();

  // Arabic CV
  if (lower.contains('arabic cv')) return l10n.errorArabicCV;

  // Invalid CV
  if (lower.contains('not a valid cv') ||
      lower.contains('not appear to be a valid cv')) {
    return l10n.errorInvalidCV;
  }

  // Image-based PDF (scanned)
  if (lower.contains('image-based') || lower.contains('no extractable text')) {
    return l10n.errorImagePDF;
  }

  // Old .doc format
  if (lower.contains('.doc format') || lower.contains('office 97')) {
    return l10n.errorOldDocFormat;
  }

  // File type not allowed
  if (lower.contains('file type not allowed') ||
      lower.contains('unsupported file type')) {
    return l10n.errorUnsupportedFormat;
  }

  // Quota / rate limit
  if (lower.contains('quota exceeded') || lower.contains('rate limit')) {
    return l10n.errorQuotaExceeded;
  }

  return null; // No match — use raw detail
}
