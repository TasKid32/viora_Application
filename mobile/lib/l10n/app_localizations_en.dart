// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appName => 'viora';

  @override
  String get appTagline => 'Together, we shape your vision.';

  @override
  String get appDeveloper =>
      'Developed by Viora Team - Al-Jouf University ©2026';

  @override
  String get getStarted => 'Get Started';

  @override
  String get welcomeBack => 'Welcome back';

  @override
  String get signInToContinue => 'Sign in to continue';

  @override
  String get email => 'Email';

  @override
  String get emailHint => 'you@example.com';

  @override
  String get password => 'Password';

  @override
  String get signIn => 'Sign In';

  @override
  String get dontHaveAccount => 'Don\'t have an account? ';

  @override
  String get signUp => 'Sign Up';

  @override
  String get pleaseEnterEmail => 'Please enter your email';

  @override
  String get pleaseEnterValidEmail => 'Please enter a valid email';

  @override
  String get pleaseEnterPassword => 'Please enter your password';

  @override
  String get passwordMinLength => 'Password must be at least 6 characters';

  @override
  String get joinViora => 'Join viora';

  @override
  String get startCareerJourney => 'Start your career journey today';

  @override
  String get fullName => 'Full Name';

  @override
  String get fullNameHint => 'Tasneem AlNashmi';

  @override
  String get confirmPassword => 'Confirm Password';

  @override
  String get createAccount => 'Create Account';

  @override
  String get alreadyHaveAccount => 'Already have an account? ';

  @override
  String get logIn => 'Log In';

  @override
  String get pleaseEnterName => 'Please enter your name';

  @override
  String get pleaseConfirmPassword => 'Please confirm your password';

  @override
  String get passwordsDoNotMatch => 'Passwords do not match';

  @override
  String get forgotPasswordTitle => 'Forgot Password?';

  @override
  String get forgotPasswordDescription =>
      'Don\'t worry! Enter your email address and we\'ll send you a link to reset your password.';

  @override
  String get emailAddress => 'Email Address';

  @override
  String get enterYourEmail => 'Enter your email';

  @override
  String get sendResetLink => 'Send Reset Link';

  @override
  String get backToSignIn => 'Back to Sign In';

  @override
  String get checkYourEmail => 'Check Your Email';

  @override
  String get resetLinkSent => 'We\'ve sent a password reset link to:';

  @override
  String get didntReceiveEmail => 'Didn\'t receive the email?';

  @override
  String get checkSpamOrRetry => 'Check your spam folder or try again';

  @override
  String get resendEmail => 'Resend Email';

  @override
  String get resetLinkSentSuccess => 'Password reset link sent successfully!';

  @override
  String failedToSendResetLink(String error) {
    return 'Failed to send reset link: $error';
  }

  @override
  String hello(String name) {
    return 'Hello, $name ';
  }

  @override
  String get readyToGrow => 'Ready to grow your skills today?';

  @override
  String get yourProgress => 'Your Progress';

  @override
  String get retry => 'Retry';

  @override
  String get skillAnalysis => 'Skill Analysis';

  @override
  String get careerPath => 'Career Path';

  @override
  String get training => 'Training';

  @override
  String get smartAssistant => 'Smart Assistant';

  @override
  String get myCourses => 'My Courses';

  @override
  String coursesCount(int count) {
    return '$count courses';
  }

  @override
  String get searchCourses => 'Search courses...';

  @override
  String get all => 'All';

  @override
  String get inProgress => 'In Progress';

  @override
  String get completed => 'Completed';

  @override
  String get failedToLoadCourses => 'Failed to load courses';

  @override
  String get unknownError => 'Unknown error';

  @override
  String get noCoursesFound => 'No courses found';

  @override
  String get addFirstCourse => 'Add your first course to get started';

  @override
  String get continueLearning => 'Continue Learning';

  @override
  String get edit => 'Edit';

  @override
  String get delete => 'Delete';

  @override
  String get addNewCourse => 'Add New Course';

  @override
  String get courseTitle => 'Course Title';

  @override
  String get category => 'Category';

  @override
  String get platform => 'Platform';

  @override
  String get cancel => 'Cancel';

  @override
  String get add => 'Add';

  @override
  String get updateProgress => 'Update Progress';

  @override
  String get completionPercent => 'Completion (%)';

  @override
  String get update => 'Update';

  @override
  String get deleteCourse => 'Delete Course';

  @override
  String deleteCourseConfirmation(String title) {
    return 'Are you sure you want to delete \"$title\"?';
  }

  @override
  String get failedToLoadCourse => 'Failed to load course';

  @override
  String get courseNotFound => 'Course not found';

  @override
  String get enrolled => 'Enrolled';

  @override
  String get notEnrolled => 'Not enrolled';

  @override
  String get courseProgress => 'Course Progress';

  @override
  String get courseDetails => 'Course Details';

  @override
  String get title => 'Title';

  @override
  String get status => 'Status';

  @override
  String get markAsCompleted => 'Mark as Completed';

  @override
  String get notStarted => 'Not Started';

  @override
  String get uploadCV => 'Upload Your CV';

  @override
  String get uploadCVDesc => 'Upload your CV to analyze your skills';

  @override
  String get selectFile => 'Select File';

  @override
  String get uploadAndAnalyze => 'Upload & Analyze';

  @override
  String get analyzing => 'Analyzing...';

  @override
  String get analysisComplete => 'Analysis Complete';

  @override
  String get yourSkills => 'Your Skills';

  @override
  String get generateRoadmap => 'Generate Roadmap';

  @override
  String get noSkillsFound => 'No skills found';

  @override
  String get pleaseUploadCV => 'Please upload your CV first';

  @override
  String get analysisInProgress => 'Analysis in progress...';

  @override
  String get pleaseWait => 'Please wait while we analyze your CV';

  @override
  String skillsFound(int count) {
    return '$count skills found';
  }

  @override
  String get manualSkillEntry => 'Or enter skills manually';

  @override
  String get enterSkill => 'Enter a skill';

  @override
  String get addSkill => 'Add Skill';

  @override
  String get submitSkills => 'Submit Skills';

  @override
  String get trackYourProgress => 'Your Progress';

  @override
  String get trackLearningJourney => 'Track your learning journey';

  @override
  String get skillGrowth => 'Skill Growth';

  @override
  String get weeklyActivity => 'Weekly Activity';

  @override
  String get noActivityData => 'No activity data available';

  @override
  String get completedCourses => 'Completed Courses';

  @override
  String get noCompletedCourses => 'No completed courses yet';

  @override
  String get notifications => 'Notifications';

  @override
  String newNotificationsCount(int count) {
    return '$count new notifications';
  }

  @override
  String get markAllRead => 'Mark all read';

  @override
  String get noNotificationsYet => 'No notifications yet';

  @override
  String get notificationsEmptyDesc =>
      'You\'ll see notifications here when you have updates';

  @override
  String get notificationDeleted => 'Notification deleted';

  @override
  String get failedToLoadNotifications => 'Failed to load notifications';

  @override
  String get failedToMarkAsRead => 'Failed to mark as read';

  @override
  String get failedToDeleteNotification => 'Failed to delete notification';

  @override
  String get allMarkedAsRead => 'All notifications marked as read';

  @override
  String get failedToMarkAllRead => 'Failed to mark all as read';

  @override
  String get justNow => 'Just now';

  @override
  String minutesAgo(int count) {
    return '$count minutes ago';
  }

  @override
  String hoursAgo(int count) {
    return '$count hours ago';
  }

  @override
  String get yesterday => 'Yesterday';

  @override
  String daysAgo(int count) {
    return '$count days ago';
  }

  @override
  String unreadNotifications(int count) {
    return 'You have $count unread notifications';
  }

  @override
  String get stayUpdated => 'Stay updated with your progress';

  @override
  String get settings => 'Settings';

  @override
  String get manageAccount => 'Manage your account';

  @override
  String get editProfile => 'Edit Profile';

  @override
  String get updateYourInfo => 'Update your information';

  @override
  String get notificationSettings => 'Notifications';

  @override
  String get manageAlerts => 'Manage your alerts';

  @override
  String get privacySecurity => 'Privacy & Security';

  @override
  String get keepDataSafe => 'Keep your data safe';

  @override
  String get language => 'Language';

  @override
  String get arabic => 'Arabic';

  @override
  String get english => 'English';

  @override
  String get helpSupport => 'Help & Support';

  @override
  String get getAssistance => 'Get assistance';

  @override
  String get loading => 'Loading...';

  @override
  String get failedToLoadProfile => 'Failed to load profile';

  @override
  String get phone => 'Phone';

  @override
  String get bio => 'Bio';

  @override
  String get saveChanges => 'Save Changes';

  @override
  String get profileUpdatedSuccess => 'Profile updated successfully';

  @override
  String failedToUpdateProfile(String error) {
    return 'Failed to update profile: $error';
  }

  @override
  String get changePassword => 'Change Password';

  @override
  String get passwordMinLength8 =>
      'Your password must be at least 8 characters long';

  @override
  String get currentPassword => 'Current Password';

  @override
  String get enterCurrentPassword => 'Enter current password';

  @override
  String get newPassword => 'New Password';

  @override
  String get enterNewPassword => 'Enter new password';

  @override
  String get confirmNewPassword => 'Confirm New Password';

  @override
  String get confirmNewPasswordHint => 'Confirm new password';

  @override
  String get pleaseEnterCurrentPassword => 'Please enter your current password';

  @override
  String get pleaseEnterNewPassword => 'Please enter a new password';

  @override
  String get passwordMin8Chars => 'Password must be at least 8 characters';

  @override
  String get newPasswordMustDiffer =>
      'New password must be different from current';

  @override
  String get pleaseConfirmNewPassword => 'Please confirm your new password';

  @override
  String get passwordChangedSuccess => 'Password changed successfully!';

  @override
  String failedToChangePassword(String error) {
    return 'Failed to change password: $error';
  }

  @override
  String get weak => 'Weak';

  @override
  String get fair => 'Fair';

  @override
  String get good => 'Good';

  @override
  String get strong => 'Strong';

  @override
  String get atLeast8Chars => 'At least 8 characters';

  @override
  String get containsUppercase => 'Contains uppercase letter';

  @override
  String get containsLowercase => 'Contains lowercase letter';

  @override
  String get containsNumber => 'Contains number';

  @override
  String get selectLanguage => 'Select Language';

  @override
  String get languageUpdatedSuccess => 'Language updated successfully';

  @override
  String get notificationSettingsTitle => 'Notification Settings';

  @override
  String get general => 'General';

  @override
  String get pushNotifications => 'Push Notifications';

  @override
  String get receivePushNotifications => 'Receive push notifications';

  @override
  String get emailNotifications => 'Email Notifications';

  @override
  String get receiveEmailUpdates => 'Receive email updates';

  @override
  String get notificationTypes => 'Notification Types';

  @override
  String get courseUpdates => 'Course Updates';

  @override
  String get newCoursesContent => 'New courses and content';

  @override
  String get progressReports => 'Progress Reports';

  @override
  String get weeklyProgressSummary => 'Weekly progress summary';

  @override
  String get achievements => 'Achievements';

  @override
  String get badgesAndRewards => 'Badges and rewards';

  @override
  String get recommendations => 'Recommendations';

  @override
  String get personalizedSuggestions => 'Personalized suggestions';

  @override
  String get security => 'Security';

  @override
  String get updateYourPassword => 'Update your password';

  @override
  String get twoFactorAuth => 'Two-Factor Authentication';

  @override
  String get extraSecurityLayer => 'Extra security layer';

  @override
  String get biometricLogin => 'Biometric Login';

  @override
  String get useFingerprintOrFace => 'Use fingerprint or face';

  @override
  String get privacy => 'Privacy';

  @override
  String get profileVisibility => 'Profile Visibility';

  @override
  String get whoCanSeeProfile => 'Who can see your profile';

  @override
  String get profileVisibilityComingSoon =>
      'Profile visibility settings coming soon.';

  @override
  String get downloadMyData => 'Download My Data';

  @override
  String get getCopyOfData => 'Get a copy of your data';

  @override
  String get dataDownloadComingSoon => 'Data download feature coming soon.';

  @override
  String get account => 'Account';

  @override
  String get logout => 'Logout';

  @override
  String get signOutOfAccount => 'Sign out of your account';

  @override
  String get logoutConfirmation => 'Are you sure you want to logout?';

  @override
  String get deleteAccount => 'Delete Account';

  @override
  String get permanentlyDeleteAccount => 'Permanently delete account';

  @override
  String get deleteAccountWarning =>
      'This action cannot be undone. All your data will be permanently deleted.';

  @override
  String get accountDeletionNotAvailable =>
      'Account deletion is not yet available.';

  @override
  String get getHelp => 'Get Help';

  @override
  String get faqs => 'FAQs';

  @override
  String get frequentlyAskedQuestions => 'Frequently asked questions';

  @override
  String get liveChat => 'Live Chat';

  @override
  String get chatWithSupport => 'Chat with support team';

  @override
  String get emailSupport => 'Email Support';

  @override
  String get resources => 'Resources';

  @override
  String get videoTutorials => 'Video Tutorials';

  @override
  String get learnHowToUse => 'Learn how to use Viora';

  @override
  String get userGuide => 'User Guide';

  @override
  String get completeDocumentation => 'Complete documentation';

  @override
  String get about => 'About';

  @override
  String get aboutViora => 'About Viora';

  @override
  String get versionInfo => 'Version 1.0.0';

  @override
  String get termsOfService => 'Terms of Service';

  @override
  String get readOurTerms => 'Read our terms';

  @override
  String get privacyPolicy => 'Privacy Policy';

  @override
  String get howWeProtectData => 'How we protect your data';

  @override
  String comingSoon(String feature) {
    return '$feature coming soon.';
  }

  @override
  String get aiAssistant => 'AI Assistant';

  @override
  String get askMeAnything => 'Ask me anything about your career...';

  @override
  String get typeMessage => 'Type your message...';

  @override
  String get errorNetwork => 'Network error occurred';

  @override
  String get errorServer => 'Server error occurred';

  @override
  String get errorUnauthorized => 'Session expired. Please login again';

  @override
  String get errorTimeout => 'Request timed out';

  @override
  String get errorUnknown => 'An unexpected error occurred';

  @override
  String get languageUpdated => 'Language updated successfully';

  @override
  String get navHome => 'Home';

  @override
  String get navProgress => 'Progress';

  @override
  String get navAssistant => 'Assistant';

  @override
  String get navProfile => 'Profile';

  @override
  String get smartAssistantTitle => 'Smart Assistant';

  @override
  String get alwaysHereToHelp => 'Always here to help';

  @override
  String get quickActions => 'Quick actions:';

  @override
  String get analyzeCV => 'Analyze CV';

  @override
  String get helpAnalyzeCV => 'Help me analyze my CV';

  @override
  String get careerAdvice => 'Career Advice';

  @override
  String get giveCareerAdvice => 'Give me career advice based on my skills';

  @override
  String get findCourses => 'Find Courses';

  @override
  String get recommendCourses => 'Recommend courses to improve my skills';

  @override
  String get hiHowCanIHelp => 'Hi! How can I assist you today?';

  @override
  String get askAboutCareer => 'Ask me anything about your career development';

  @override
  String get failedToLoadCourseDetails => 'Failed to load course';

  @override
  String get courseNotFoundMsg => 'Course not found';

  @override
  String get enrolledLabel => 'Enrolled';

  @override
  String get completedLabel => 'Completed';

  @override
  String get notEnrolledLabel => 'Not enrolled';

  @override
  String get courseProgressTitle => 'Course Progress';

  @override
  String get courseDetailsTitle => 'Course Details';

  @override
  String get titleLabel => 'Title';

  @override
  String get categoryLabel => 'Category';

  @override
  String get platformLabel => 'Platform';

  @override
  String get statusLabel => 'Status';

  @override
  String get markAsCompletedBtn => 'Mark as Completed';

  @override
  String get deleteCourseBtn => 'Delete Course';

  @override
  String get deleteBtn => 'Delete';

  @override
  String get notStartedStatus => 'Not Started';

  @override
  String get inProgressStatus => 'In Progress';

  @override
  String get completedStatus => 'Completed';

  @override
  String areYouSureDeleteCourse(String title) {
    return 'Are you sure you want to delete \"$title\"?';
  }

  @override
  String get failedToLoadRoadmap => 'Failed to load roadmap';

  @override
  String get noRoadmapAvailable => 'No roadmap available';

  @override
  String get completeSkillsFirst => 'Complete your skills analysis first';

  @override
  String get learningRoadmap => 'Learning Roadmap';

  @override
  String get personalizedPath => 'Your personalized learning path';

  @override
  String get overallProgress => 'Overall Progress';

  @override
  String phasesProgress(int completed, int total) {
    return '$completed of $total phases';
  }

  @override
  String get learningPhases => 'Learning Phases';

  @override
  String duration(String value) {
    return 'Duration: $value';
  }

  @override
  String topicsCount(int count) {
    return '$count topics';
  }

  @override
  String get recommendedResources => 'Recommended Resources:';

  @override
  String get skillAnalysisTitle => 'Skill Analysis';

  @override
  String get orText => 'Or';

  @override
  String get uploadResume => 'Upload Resume';

  @override
  String get resumeSelected => 'Resume Selected';

  @override
  String get pdfDocDocx => 'PDF, DOC, or DOCX';

  @override
  String get removeFile => 'Remove file';

  @override
  String get orTypeSkills => 'Or type your skills';

  @override
  String get skillsHintText => 'e.g., JavaScript, React, TypeScript...';

  @override
  String get analyzeNow => 'Analyze Now';

  @override
  String errorSelectingFile(String error) {
    return 'Error selecting file: $error';
  }

  @override
  String get pleaseUploadOrEnter =>
      'Please upload a resume or enter your skills manually';

  @override
  String get analysisCompletedSuccess => 'Analysis completed successfully!';

  @override
  String get analyzingResume => 'Analyzing your resume...';

  @override
  String get mayTakeMoments => 'This may take a few moments';

  @override
  String get strongSkills => 'Strong Skills';

  @override
  String get skillsToDevelop => 'Skills to Develop';

  @override
  String get predictedCareer => 'Predicted Career';

  @override
  String levelLabel(String level) {
    return '📊 Level: $level';
  }

  @override
  String get readyToCreatePath => 'Ready to Create Your Learning Path?';

  @override
  String get generatePersonalizedRoadmap =>
      'Generate a personalized roadmap based on your skills analysis';

  @override
  String get generateLearningRoadmap => 'Generate Learning Roadmap →';

  @override
  String get roadmapGenerated => '🎉 Roadmap generated! Check Progress tab';

  @override
  String get analyzingText => 'Analyzing...';

  @override
  String get careerDirection => 'Career Direction';

  @override
  String get jobOpportunities => 'Job Opportunities';

  @override
  String get basedOnProfile => 'Based on your profile:';

  @override
  String get recommendationsTitle => 'Recommendations';

  @override
  String languageChangedTo(String name) {
    return 'Language changed to $name';
  }

  @override
  String failedToUpdateLanguage(String error) {
    return 'Failed to update language: $error';
  }

  @override
  String get selectLanguageTitle => 'Select Language';

  @override
  String get languageTitle => 'Language';

  @override
  String get dayMon => 'Mon';

  @override
  String get dayTue => 'Tue';

  @override
  String get dayWed => 'Wed';

  @override
  String get dayThu => 'Thu';

  @override
  String get dayFri => 'Fri';

  @override
  String get daySat => 'Sat';

  @override
  String get daySun => 'Sun';

  @override
  String get startJourneyTitle => 'Start Your Career Journey!';

  @override
  String get startJourneyDesc =>
      'Upload your CV to discover your skills and get a personalized learning path.';

  @override
  String get analyzeMyCV => 'Analyze My CV →';

  @override
  String get roadmapReadyTitle => 'Your Learning Path is Ready!';

  @override
  String get roadmapReadyDesc =>
      'View your personalized roadmap and start learning.';

  @override
  String get viewRoadmap => 'View Roadmap →';

  @override
  String get newAnalysis => 'New Analysis';

  @override
  String roadmapStepsProgress(Object completed, Object total) {
    return '$completed/$total steps';
  }

  @override
  String coursesProgress(Object completed, Object total) {
    return '$completed/$total courses';
  }

  @override
  String get analyzeFirst =>
      'Analyze your CV first to get a personalized learning path.';

  @override
  String get goToAnalysis => 'Go to Analysis';

  @override
  String get autoGeneratingRoadmap => 'Generating your learning path...';

  @override
  String get navAnalysis => 'Analysis Skills';

  @override
  String get navRoadmap => 'Roadmap';

  @override
  String get navAdvisor => 'Advisor';

  @override
  String get resumeQuality => 'Resume Quality';

  @override
  String get excellent => 'Excellent';

  @override
  String get acceptable => 'Acceptable';

  @override
  String wordsCount(int count) {
    return '$count words';
  }

  @override
  String get uploadingResume => 'Uploading Your Resume...';

  @override
  String get extractingText => 'Extracting Text...';

  @override
  String get aiSkillAnalysis => 'Analyzing Skills with AI...';

  @override
  String get careerMatching => 'Matching Career Database...';

  @override
  String get processing => 'Processing...';

  @override
  String get uploadingDesc => 'Securely uploading your CV to the server';

  @override
  String get extractingDesc =>
      'Reading and extracting content from your document';

  @override
  String get analyzingDesc =>
      'Our AI model is identifying your skills and experience';

  @override
  String get matchingDesc =>
      'Comparing your profile with O*NET career standards';

  @override
  String get processingDesc => 'Please wait while we process your resume';

  @override
  String get usuallyTakes => 'Usually takes 30–60 seconds';

  @override
  String get uploadFile => 'Upload File';

  @override
  String get extractText => 'Extract Text';

  @override
  String get createLearningPath => 'Create Learning Path';

  @override
  String get generatingPath => 'Generating...';

  @override
  String get profilePhotoUpdated => 'Profile photo updated ✅';

  @override
  String get failedUploadPhoto => 'Failed to upload photo';

  @override
  String get showLess => 'Show Less';

  @override
  String get couldNotOpenLink => 'Could not open this link';

  @override
  String showMoreResources(int count) {
    return 'Show $count More Resources';
  }

  @override
  String get showMore => 'Show More';

  @override
  String get reanalysisWarningTitle => 'Re-analyze CV?';

  @override
  String get reanalysisWarningBody =>
      'This will archive your previous analysis and roadmap, and clear your chat history to focus on the new CV.';

  @override
  String get continueText => 'Continue';

  @override
  String get languages => 'Languages';

  @override
  String get strengths => 'Strengths';

  @override
  String fileTooLarge(String size) {
    return 'File too large (${size}MB). Maximum size is 10MB.';
  }

  @override
  String get tapToSelectFile => 'Tap to select a file';

  @override
  String get pdfDocxUpTo10 => 'PDF, DOCX — up to 10MB';

  @override
  String get newChat => 'New Chat';

  @override
  String get couldNotConnectAssistant => 'Could not connect to assistant';

  @override
  String get videos => 'Videos';

  @override
  String get courses => 'Courses';

  @override
  String get phaseCompleted => 'Phase Completed!';

  @override
  String get of_ => 'of';

  @override
  String get resourcesCompleted => 'completed';

  @override
  String get resourcesTotal => 'resources';

  @override
  String get articles => 'Articles';

  @override
  String get phases => 'Phases';

  @override
  String get techSkills => 'Technical Tools';

  @override
  String get hardSkills => 'Core Competencies';

  @override
  String get softSkills => 'Professional Skills';

  @override
  String get errorArabicCV =>
      'Please upload an English CV. Arabic CVs are not supported yet.';

  @override
  String get errorInvalidCV =>
      'The uploaded file doesn\'t appear to be a valid CV. Please check and try again.';

  @override
  String get errorImagePDF =>
      'This PDF is image-based (scanned). Please upload a text-based PDF or DOCX.';

  @override
  String get errorOldDocFormat =>
      'Old .doc format is not supported. Please convert to .docx or .pdf.';

  @override
  String get errorUnsupportedFormat =>
      'Unsupported file format. Please use PDF or DOCX.';

  @override
  String get errorQuotaExceeded =>
      'Service temporarily unavailable due to high demand. Please try again later.';

  @override
  String get errorFileTooLarge => 'File is too large. Maximum size is 10MB.';

  @override
  String get errorConnectionTimeout =>
      'Connection timed out. Please check your internet connection.';

  @override
  String get errorNoConnection =>
      'Could not connect to server. Please check your internet connection.';

  @override
  String get errorAnalysisTimeout =>
      'Analysis took too long. Please try again.';

  @override
  String get errorGeneric => 'An error occurred. Please try again.';

  @override
  String get phoneNumber => 'Phone Number';

  @override
  String get bioHint => 'Tell us about yourself...';

  @override
  String get memberSince => 'Member since';

  @override
  String get topics => 'Topics';

  @override
  String get yourJourney => 'Your Journey';

  @override
  String get cvAnalyzed => 'CV Analyzed';

  @override
  String get roadmapReady => 'Roadmap Generated';

  @override
  String get learningStarted => 'Learning in Progress';

  @override
  String get phaseNotFound => 'Phase not found';

  @override
  String showAllCount(int count) {
    return 'Show all ($count)';
  }

  @override
  String get appCopyright => '© 2026 Viora';

  @override
  String get appDescription =>
      'AI-powered career development and skills analysis app';
}
