/// API endpoint constants — matches Backend router paths.
class Endpoints {
  Endpoints._();

  static const _api = '/api';

  // ── Auth ──────────────────────────────────────────────
  static const String register = '$_api/auth/register';
  static const String login    = '$_api/auth/login';
  static const String refresh  = '$_api/auth/refresh';
  static const String forgotPassword = '$_api/auth/forgot-password';

  // ── Resume (single endpoint!) ─────────────────────────
  static const String resumeUpload  = '$_api/resume/upload';
  static const String resumeAnalyze       = '$_api/resume/analyze';
  static const String resumeAnalyzeStream = '$_api/resume/analyze/stream';
  static const String resumeSkills  = '$_api/resume/skills';

  // ── Dashboard ─────────────────────────────────────────
  static const String dashboard = '$_api/dashboard';

  // ── Roadmap ───────────────────────────────────────────
  static const String roadmap         = '$_api/roadmap';
  static const String roadmapGenerate = '$_api/roadmap/generate';
  static String roadmapStepComplete(int index) => '$_api/roadmap/steps/$index/complete';
  static String roadmapStepIncomplete(int index) => '$_api/roadmap/steps/$index/incomplete';
  static String roadmapResourceToggle(int phaseIndex, dynamic resourceId) =>
      '$_api/roadmap/steps/$phaseIndex/resources/$resourceId/toggle';

  // ── Progress (NOT YET IMPLEMENTED in backend) ─────────
  // static const String weeklyActivity = '$_api/progress/weekly';

  // ── Courses ───────────────────────────────────────────
  static const String courses = '$_api/courses';
  static String course(String id) => '$_api/courses/$id';

  // ── Chat ──────────────────────────────────────────────
  static const String chatSend    = '$_api/chat/send';
  static const String chatHistory = '$_api/chat/history';
  static const String chatClear   = '$_api/chat/history';

  // ── Profile ───────────────────────────────────────────
  static const String profile       = '$_api/profile';
  static const String profileAvatar = '$_api/profile/avatar';
  static const String language = '$_api/profile/settings/language';

  // ── Notifications ─────────────────────────────────────
  static const String notifications = '$_api/notifications';
  static String notificationRead(String id) => '$_api/notifications/$id/read';
}
