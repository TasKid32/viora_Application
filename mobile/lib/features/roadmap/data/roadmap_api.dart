import 'package:dio/dio.dart';
import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';

/// Resource in a roadmap phase (YouTube, official docs, courses, articles).
class LearningResource {
  final String type;  // 'video', 'course', 'article', 'official_doc', 'course_search'
  final String title;
  final String url;
  final String platform;
  final String? thumbnail;
  final String? channel;
  final String? duration;
  final String? description;
  final String? source;
  bool completed;

  LearningResource({
    required this.type,
    required this.title,
    required this.url,
    required this.platform,
    this.thumbnail,
    this.channel,
    this.duration,
    this.description,
    this.source,
    this.completed = false,
  });

  factory LearningResource.fromJson(Map<String, dynamic> json) => LearningResource(
    type: json['type'] as String? ?? 'course',
    title: json['title'] as String? ?? '',
    url: json['url'] as String? ?? '',
    platform: json['platform'] as String? ?? 'Web',
    thumbnail: json['thumbnail'] as String?,
    channel: json['channel'] as String?,
    duration: json['duration'] as String?,
    description: json['description'] as String?,
    source: json['source'] as String?,
    completed: json['completed'] as bool? ?? false,
  );
}

/// A topic with its own grouped resources (NEW per-topic structure).
class TopicResources {
  final String name;
  final List<LearningResource> resources;

  bool get completed => resources.isNotEmpty && resources.every((r) => r.completed);
  int get completedCount => resources.where((r) => r.completed).length;

  TopicResources({required this.name, required this.resources});

  factory TopicResources.fromJson(dynamic raw) {
    // Handle BOTH old format (string) and new format (map)
    if (raw is String) {
      return TopicResources(name: raw, resources: []);
    }
    final json = raw as Map<String, dynamic>;
    final rawResources = json['resources'] as List? ?? [];
    return TopicResources(
      name: json['name'] as String? ?? '',
      resources: rawResources
          .map((r) => LearningResource.fromJson(r as Map<String, dynamic>))
          .toList(),
    );
  }
}

/// A learning phase in the roadmap.
class RoadmapPhase {
  final String phase;
  final String duration;
  final String priority;
  final List<TopicResources> topics;
  bool completed;

  /// Flatten all resources across all topics for progress calculations.
  List<LearningResource> get allResources =>
      topics.expand((t) => t.resources).toList();

  /// Legacy compat: old code references phase.resources directly.
  /// Now it's just a flattened view of all topic resources.
  List<LearningResource> get resources => allResources;

  RoadmapPhase({
    required this.phase,
    required this.duration,
    required this.priority,
    required this.topics,
    this.completed = false,
  });

  factory RoadmapPhase.fromJson(Map<String, dynamic> json) {
    final rawTopics = json['topics'] as List? ?? [];

    List<TopicResources> parsedTopics;

    // Check if topics contain objects (new) or strings (old)
    if (rawTopics.isNotEmpty && rawTopics.first is Map) {
      // NEW format: topics are {name, resources[]}
      parsedTopics = rawTopics.map((t) => TopicResources.fromJson(t)).toList();
    } else {
      // OLD format: topics are strings, resources are flat in phase
      final oldResources = (json['resources'] as List? ?? [])
          .map((r) => LearningResource.fromJson(r as Map<String, dynamic>))
          .toList();

      if (rawTopics.isNotEmpty && oldResources.isNotEmpty) {
        // Distribute old resources across topics evenly
        final topicNames = rawTopics.map((t) => t.toString()).toList();
        final perTopic = (oldResources.length / topicNames.length).ceil();
        parsedTopics = [];
        for (int i = 0; i < topicNames.length; i++) {
          final start = i * perTopic;
          final end = (start + perTopic).clamp(0, oldResources.length);
          parsedTopics.add(TopicResources(
            name: topicNames[i],
            resources: start < oldResources.length
                ? oldResources.sublist(start, end)
                : [],
          ));
        }
      } else {
        parsedTopics = rawTopics.map((t) => TopicResources.fromJson(t)).toList();
      }
    }

    return RoadmapPhase(
      phase: json['phase'] as String? ?? '',
      duration: json['duration'] as String? ?? '',
      priority: json['priority'] as String? ?? 'Medium',
      topics: parsedTopics,
      completed: json['completed'] as bool? ?? false,
    );
  }
}

/// Roadmap data from Backend.
class RoadmapData {
  final String roadmapId;
  final List<RoadmapPhase> phases;

  const RoadmapData({required this.roadmapId, required this.phases});

  factory RoadmapData.fromJson(Map<String, dynamic> json) {
    final rawPhases = json['learning_roadmap'] as List? ?? [];
    return RoadmapData(
      roadmapId: json['roadmap_id'] as String? ?? '',
      phases: rawPhases.map((p) => RoadmapPhase.fromJson(p as Map<String, dynamic>)).toList(),
    );
  }
}

/// Roadmap API.
class RoadmapApi {
  final ApiClient _api;
  RoadmapApi(this._api);

  Future<RoadmapData> getRoadmap({String? analysisId}) async {
    final response = await _api.get(
      Endpoints.roadmap,
      params: analysisId != null ? {'analysis_id': analysisId} : null,
    );
    return RoadmapData.fromJson(response.data);
  }

  Future<RoadmapData> generateRoadmap(String analysisId) async {
    final response = await _api.post(
      Endpoints.roadmapGenerate,
      data: {'analysis_id': analysisId},
      options: Options(receiveTimeout: const Duration(seconds: 180)),
    );
    return RoadmapData.fromJson(response.data);
  }

  Future<void> markStepComplete(int index) async {
    await _api.put(Endpoints.roadmapStepComplete(index));
  }

  Future<void> markStepIncomplete(int index) async {
    await _api.put(Endpoints.roadmapStepIncomplete(index));
  }

  Future<Map<String, dynamic>> toggleResource(int phaseIndex, int resourceIndex, {String? resourceId}) async {
    final endpoint = resourceId != null
        ? Endpoints.roadmapResourceToggle(phaseIndex, resourceId)
        : Endpoints.roadmapResourceToggle(phaseIndex, resourceIndex.toString());
    final response = await _api.put(endpoint);
    return response.data as Map<String, dynamic>;
  }
}
