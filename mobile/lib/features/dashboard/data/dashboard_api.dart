import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';

/// Dashboard data model — real progress tracking.
class DashboardData {
  final String userName;
  final String userEmail;
  final String? avatarUrl;
  final int learningProgress;  // 0-100, purely resource-based
  final String journeyStep;    // "new" | "analyzed" | "roadmap_ready" | "learning"
  final int skillsFound;
  final bool hasAnalysis;
  final bool hasRoadmap;
  final int totalCourses;
  final int completedCourses;
  final int notificationsCount;
  final int roadmapStepsTotal;
  final int roadmapStepsCompleted;
  final int roadmapResourcesTotal;
  final int roadmapResourcesCompleted;
  final int topicsTotal;
  final int topicsCompleted;

  // Legacy compat
  int get overallProgress => learningProgress;
  int get skillGrowth => skillsFound;

  const DashboardData({
    required this.userName,
    required this.userEmail,
    this.avatarUrl,
    required this.learningProgress,
    required this.journeyStep,
    required this.skillsFound,
    required this.hasAnalysis,
    required this.hasRoadmap,
    required this.totalCourses,
    required this.completedCourses,
    required this.notificationsCount,
    required this.roadmapStepsTotal,
    required this.roadmapStepsCompleted,
    required this.roadmapResourcesTotal,
    required this.roadmapResourcesCompleted,
    required this.topicsTotal,
    required this.topicsCompleted,
  });

  factory DashboardData.fromJson(Map<String, dynamic> json) {
    final user = json['user'] as Map<String, dynamic>? ?? {};
    final progress = json['progress'] as Map<String, dynamic>? ?? {};

    return DashboardData(
      userName: user['name'] as String? ?? 'User',
      userEmail: user['email'] as String? ?? '',
      avatarUrl: user['profile_picture'] as String?,
      learningProgress: progress['learning_progress'] as int?
          ?? progress['overall_percentage'] as int? ?? 0,
      journeyStep: progress['journey_step'] as String? ?? 'new',
      skillsFound: progress['skills_found'] as int?
          ?? progress['skill_growth'] as int? ?? 0,
      hasAnalysis: progress['has_analysis'] as bool? ?? false,
      hasRoadmap: progress['has_roadmap'] as bool? ?? false,
      totalCourses: progress['total_courses'] as int? ?? 0,
      completedCourses: progress['completed_courses_count'] as int? ?? 0,
      notificationsCount: json['notifications_count'] as int? ?? 0,
      roadmapStepsTotal: progress['roadmap_steps_total'] as int? ?? 0,
      roadmapStepsCompleted: progress['roadmap_steps_completed'] as int? ?? 0,
      roadmapResourcesTotal: progress['roadmap_resources_total'] as int? ?? 0,
      roadmapResourcesCompleted: progress['roadmap_resources_completed'] as int? ?? 0,
      topicsTotal: progress['topics_total'] as int? ?? 0,
      topicsCompleted: progress['topics_completed'] as int? ?? 0,
    );
  }
}

/// Dashboard API.
class DashboardApi {
  final ApiClient _api;
  DashboardApi(this._api);

  Future<DashboardData> getDashboard() async {
    final response = await _api.get(Endpoints.dashboard);
    return DashboardData.fromJson(response.data);
  }
}
