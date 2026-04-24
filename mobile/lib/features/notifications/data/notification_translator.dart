import 'package:viora_app/l10n/app_localizations.dart';

/// Runtime translator: maps notification keys → l10n methods.
///
/// The backend sends `title_key`, `message_key`, and `data`.
/// This class uses the generated AppLocalizations to produce localized text,
/// falling back to the raw English `title`/`message` if the key is unknown.
class NotificationTranslator {
  NotificationTranslator._();

  /// Translate a notification title.
  static String title(
    AppLocalizations l10n,
    String? titleKey,
    String fallback,
    Map<String, dynamic>? data,
  ) {
    if (titleKey == null) return fallback;
    switch (titleKey) {
      case 'notif_welcome_title':
        return l10n.notifWelcomeTitle(data?['full_name']?.toString() ?? '');
      case 'notif_cv_analysis_title':
        return l10n.notifCvAnalysisTitle;
      case 'notif_roadmap_title':
        return l10n.notifRoadmapTitle;
      case 'notif_course_completed_title':
        return l10n.notifCourseCompletedTitle;
      case 'notif_profile_updated_title':
        return l10n.notifProfileUpdatedTitle;
      case 'notif_phase_completed_title':
        return l10n.notifPhaseCompletedTitle;
      default:
        return fallback;
    }
  }

  /// Translate a notification message.
  static String message(
    AppLocalizations l10n,
    String? messageKey,
    String fallback,
    Map<String, dynamic>? data,
  ) {
    if (messageKey == null) return fallback;
    switch (messageKey) {
      case 'notif_welcome_message':
        return l10n.notifWelcomeMessage;
      case 'notif_cv_analysis_message':
        return l10n.notifCvAnalysisMessage(
          data?['job_title']?.toString() ?? '',
          _toInt(data?['skills_found']),
          _toInt(data?['gaps_found']),
        );
      case 'notif_roadmap_message':
        return l10n.notifRoadmapMessage(
          _toInt(data?['phase_count']),
          _toInt(data?['total_topics']),
        );
      case 'notif_course_completed_message':
        return l10n.notifCourseCompletedMessage(
          data?['course_title']?.toString() ?? '',
        );
      case 'notif_profile_updated_message':
        return l10n.notifProfileUpdatedMessage;
      case 'notif_phase_completed_message':
        return l10n.notifPhaseCompletedMessage(
          data?['phase_name']?.toString() ?? '',
        );
      default:
        return fallback;
    }
  }

  /// Safely parse a dynamic value to int.
  static int _toInt(dynamic v) =>
      v is int ? v : int.tryParse(v?.toString() ?? '') ?? 0;
}