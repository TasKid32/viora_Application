import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_ar.dart';
import 'app_localizations_en.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
      : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('ar'),
    Locale('en')
  ];

  /// No description provided for @appName.
  ///
  /// In en, this message translates to:
  /// **'viora'**
  String get appName;

  /// No description provided for @appTagline.
  ///
  /// In en, this message translates to:
  /// **'Together, we shape your vision.'**
  String get appTagline;

  /// No description provided for @appDeveloper.
  ///
  /// In en, this message translates to:
  /// **'Developed by Viora Team - Al-Jouf University ©2026'**
  String get appDeveloper;

  /// No description provided for @getStarted.
  ///
  /// In en, this message translates to:
  /// **'Get Started'**
  String get getStarted;

  /// No description provided for @welcomeBack.
  ///
  /// In en, this message translates to:
  /// **'Welcome back'**
  String get welcomeBack;

  /// No description provided for @signInToContinue.
  ///
  /// In en, this message translates to:
  /// **'Sign in to continue'**
  String get signInToContinue;

  /// No description provided for @email.
  ///
  /// In en, this message translates to:
  /// **'Email'**
  String get email;

  /// No description provided for @emailHint.
  ///
  /// In en, this message translates to:
  /// **'you@example.com'**
  String get emailHint;

  /// No description provided for @password.
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get password;

  /// No description provided for @signIn.
  ///
  /// In en, this message translates to:
  /// **'Sign In'**
  String get signIn;

  /// No description provided for @dontHaveAccount.
  ///
  /// In en, this message translates to:
  /// **'Don\'t have an account? '**
  String get dontHaveAccount;

  /// No description provided for @signUp.
  ///
  /// In en, this message translates to:
  /// **'Sign Up'**
  String get signUp;

  /// No description provided for @pleaseEnterEmail.
  ///
  /// In en, this message translates to:
  /// **'Please enter your email'**
  String get pleaseEnterEmail;

  /// No description provided for @pleaseEnterValidEmail.
  ///
  /// In en, this message translates to:
  /// **'Please enter a valid email'**
  String get pleaseEnterValidEmail;

  /// No description provided for @pleaseEnterPassword.
  ///
  /// In en, this message translates to:
  /// **'Please enter your password'**
  String get pleaseEnterPassword;

  /// No description provided for @passwordMinLength.
  ///
  /// In en, this message translates to:
  /// **'Password must be at least 6 characters'**
  String get passwordMinLength;

  /// No description provided for @joinViora.
  ///
  /// In en, this message translates to:
  /// **'Join viora'**
  String get joinViora;

  /// No description provided for @startCareerJourney.
  ///
  /// In en, this message translates to:
  /// **'Start your career journey today'**
  String get startCareerJourney;

  /// No description provided for @fullName.
  ///
  /// In en, this message translates to:
  /// **'Full Name'**
  String get fullName;

  /// No description provided for @fullNameHint.
  ///
  /// In en, this message translates to:
  /// **'Tasneem AlNashmi'**
  String get fullNameHint;

  /// No description provided for @confirmPassword.
  ///
  /// In en, this message translates to:
  /// **'Confirm Password'**
  String get confirmPassword;

  /// No description provided for @createAccount.
  ///
  /// In en, this message translates to:
  /// **'Create Account'**
  String get createAccount;

  /// No description provided for @alreadyHaveAccount.
  ///
  /// In en, this message translates to:
  /// **'Already have an account? '**
  String get alreadyHaveAccount;

  /// No description provided for @logIn.
  ///
  /// In en, this message translates to:
  /// **'Log In'**
  String get logIn;

  /// No description provided for @pleaseEnterName.
  ///
  /// In en, this message translates to:
  /// **'Please enter your name'**
  String get pleaseEnterName;

  /// No description provided for @pleaseConfirmPassword.
  ///
  /// In en, this message translates to:
  /// **'Please confirm your password'**
  String get pleaseConfirmPassword;

  /// No description provided for @passwordsDoNotMatch.
  ///
  /// In en, this message translates to:
  /// **'Passwords do not match'**
  String get passwordsDoNotMatch;

  /// No description provided for @forgotPasswordTitle.
  ///
  /// In en, this message translates to:
  /// **'Forgot Password?'**
  String get forgotPasswordTitle;

  /// No description provided for @forgotPasswordDescription.
  ///
  /// In en, this message translates to:
  /// **'Don\'t worry! Enter your email address and we\'ll send you a link to reset your password.'**
  String get forgotPasswordDescription;

  /// No description provided for @emailAddress.
  ///
  /// In en, this message translates to:
  /// **'Email Address'**
  String get emailAddress;

  /// No description provided for @enterYourEmail.
  ///
  /// In en, this message translates to:
  /// **'Enter your email'**
  String get enterYourEmail;

  /// No description provided for @sendResetLink.
  ///
  /// In en, this message translates to:
  /// **'Send Reset Link'**
  String get sendResetLink;

  /// No description provided for @backToSignIn.
  ///
  /// In en, this message translates to:
  /// **'Back to Sign In'**
  String get backToSignIn;

  /// No description provided for @checkYourEmail.
  ///
  /// In en, this message translates to:
  /// **'Check Your Email'**
  String get checkYourEmail;

  /// No description provided for @resetLinkSent.
  ///
  /// In en, this message translates to:
  /// **'We\'ve sent a password reset link to:'**
  String get resetLinkSent;

  /// No description provided for @didntReceiveEmail.
  ///
  /// In en, this message translates to:
  /// **'Didn\'t receive the email?'**
  String get didntReceiveEmail;

  /// No description provided for @checkSpamOrRetry.
  ///
  /// In en, this message translates to:
  /// **'Check your spam folder or try again'**
  String get checkSpamOrRetry;

  /// No description provided for @resendEmail.
  ///
  /// In en, this message translates to:
  /// **'Resend Email'**
  String get resendEmail;

  /// No description provided for @resetLinkSentSuccess.
  ///
  /// In en, this message translates to:
  /// **'Password reset link sent successfully!'**
  String get resetLinkSentSuccess;

  /// No description provided for @failedToSendResetLink.
  ///
  /// In en, this message translates to:
  /// **'Failed to send reset link: {error}'**
  String failedToSendResetLink(String error);

  /// No description provided for @hello.
  ///
  /// In en, this message translates to:
  /// **'Hello, {name} '**
  String hello(String name);

  /// No description provided for @readyToGrow.
  ///
  /// In en, this message translates to:
  /// **'Ready to grow your skills today?'**
  String get readyToGrow;

  /// No description provided for @yourProgress.
  ///
  /// In en, this message translates to:
  /// **'Your Progress'**
  String get yourProgress;

  /// No description provided for @retry.
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get retry;

  /// No description provided for @skillAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Skill Analysis'**
  String get skillAnalysis;

  /// No description provided for @careerPath.
  ///
  /// In en, this message translates to:
  /// **'Career Path'**
  String get careerPath;

  /// No description provided for @training.
  ///
  /// In en, this message translates to:
  /// **'Training'**
  String get training;

  /// No description provided for @smartAssistant.
  ///
  /// In en, this message translates to:
  /// **'Smart Assistant'**
  String get smartAssistant;

  /// No description provided for @myCourses.
  ///
  /// In en, this message translates to:
  /// **'My Courses'**
  String get myCourses;

  /// No description provided for @coursesCount.
  ///
  /// In en, this message translates to:
  /// **'{count} courses'**
  String coursesCount(int count);

  /// No description provided for @searchCourses.
  ///
  /// In en, this message translates to:
  /// **'Search courses...'**
  String get searchCourses;

  /// No description provided for @all.
  ///
  /// In en, this message translates to:
  /// **'All'**
  String get all;

  /// No description provided for @inProgress.
  ///
  /// In en, this message translates to:
  /// **'In Progress'**
  String get inProgress;

  /// No description provided for @completed.
  ///
  /// In en, this message translates to:
  /// **'Completed'**
  String get completed;

  /// No description provided for @failedToLoadCourses.
  ///
  /// In en, this message translates to:
  /// **'Failed to load courses'**
  String get failedToLoadCourses;

  /// No description provided for @unknownError.
  ///
  /// In en, this message translates to:
  /// **'Unknown error'**
  String get unknownError;

  /// No description provided for @noCoursesFound.
  ///
  /// In en, this message translates to:
  /// **'No courses found'**
  String get noCoursesFound;

  /// No description provided for @addFirstCourse.
  ///
  /// In en, this message translates to:
  /// **'Add your first course to get started'**
  String get addFirstCourse;

  /// No description provided for @continueLearning.
  ///
  /// In en, this message translates to:
  /// **'Continue Learning'**
  String get continueLearning;

  /// No description provided for @edit.
  ///
  /// In en, this message translates to:
  /// **'Edit'**
  String get edit;

  /// No description provided for @delete.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get delete;

  /// No description provided for @addNewCourse.
  ///
  /// In en, this message translates to:
  /// **'Add New Course'**
  String get addNewCourse;

  /// No description provided for @courseTitle.
  ///
  /// In en, this message translates to:
  /// **'Course Title'**
  String get courseTitle;

  /// No description provided for @category.
  ///
  /// In en, this message translates to:
  /// **'Category'**
  String get category;

  /// No description provided for @platform.
  ///
  /// In en, this message translates to:
  /// **'Platform'**
  String get platform;

  /// No description provided for @cancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get cancel;

  /// No description provided for @add.
  ///
  /// In en, this message translates to:
  /// **'Add'**
  String get add;

  /// No description provided for @updateProgress.
  ///
  /// In en, this message translates to:
  /// **'Update Progress'**
  String get updateProgress;

  /// No description provided for @completionPercent.
  ///
  /// In en, this message translates to:
  /// **'Completion (%)'**
  String get completionPercent;

  /// No description provided for @update.
  ///
  /// In en, this message translates to:
  /// **'Update'**
  String get update;

  /// No description provided for @deleteCourse.
  ///
  /// In en, this message translates to:
  /// **'Delete Course'**
  String get deleteCourse;

  /// No description provided for @deleteCourseConfirmation.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete \"{title}\"?'**
  String deleteCourseConfirmation(String title);

  /// No description provided for @failedToLoadCourse.
  ///
  /// In en, this message translates to:
  /// **'Failed to load course'**
  String get failedToLoadCourse;

  /// No description provided for @courseNotFound.
  ///
  /// In en, this message translates to:
  /// **'Course not found'**
  String get courseNotFound;

  /// No description provided for @enrolled.
  ///
  /// In en, this message translates to:
  /// **'Enrolled'**
  String get enrolled;

  /// No description provided for @notEnrolled.
  ///
  /// In en, this message translates to:
  /// **'Not enrolled'**
  String get notEnrolled;

  /// No description provided for @courseProgress.
  ///
  /// In en, this message translates to:
  /// **'Course Progress'**
  String get courseProgress;

  /// No description provided for @courseDetails.
  ///
  /// In en, this message translates to:
  /// **'Course Details'**
  String get courseDetails;

  /// No description provided for @title.
  ///
  /// In en, this message translates to:
  /// **'Title'**
  String get title;

  /// No description provided for @status.
  ///
  /// In en, this message translates to:
  /// **'Status'**
  String get status;

  /// No description provided for @markAsCompleted.
  ///
  /// In en, this message translates to:
  /// **'Mark as Completed'**
  String get markAsCompleted;

  /// No description provided for @notStarted.
  ///
  /// In en, this message translates to:
  /// **'Not Started'**
  String get notStarted;

  /// No description provided for @uploadCV.
  ///
  /// In en, this message translates to:
  /// **'Upload Your CV'**
  String get uploadCV;

  /// No description provided for @uploadCVDesc.
  ///
  /// In en, this message translates to:
  /// **'Upload your CV to analyze your skills'**
  String get uploadCVDesc;

  /// No description provided for @selectFile.
  ///
  /// In en, this message translates to:
  /// **'Select File'**
  String get selectFile;

  /// No description provided for @uploadAndAnalyze.
  ///
  /// In en, this message translates to:
  /// **'Upload & Analyze'**
  String get uploadAndAnalyze;

  /// No description provided for @analyzing.
  ///
  /// In en, this message translates to:
  /// **'Analyzing...'**
  String get analyzing;

  /// No description provided for @analysisComplete.
  ///
  /// In en, this message translates to:
  /// **'Analysis Complete'**
  String get analysisComplete;

  /// No description provided for @yourSkills.
  ///
  /// In en, this message translates to:
  /// **'Your Skills'**
  String get yourSkills;

  /// No description provided for @generateRoadmap.
  ///
  /// In en, this message translates to:
  /// **'Generate Roadmap'**
  String get generateRoadmap;

  /// No description provided for @noSkillsFound.
  ///
  /// In en, this message translates to:
  /// **'No skills found'**
  String get noSkillsFound;

  /// No description provided for @pleaseUploadCV.
  ///
  /// In en, this message translates to:
  /// **'Please upload your CV first'**
  String get pleaseUploadCV;

  /// No description provided for @analysisInProgress.
  ///
  /// In en, this message translates to:
  /// **'Analysis in progress...'**
  String get analysisInProgress;

  /// No description provided for @pleaseWait.
  ///
  /// In en, this message translates to:
  /// **'Please wait while we analyze your CV'**
  String get pleaseWait;

  /// No description provided for @skillsFound.
  ///
  /// In en, this message translates to:
  /// **'{count} skills found'**
  String skillsFound(int count);

  /// No description provided for @manualSkillEntry.
  ///
  /// In en, this message translates to:
  /// **'Or enter skills manually'**
  String get manualSkillEntry;

  /// No description provided for @enterSkill.
  ///
  /// In en, this message translates to:
  /// **'Enter a skill'**
  String get enterSkill;

  /// No description provided for @addSkill.
  ///
  /// In en, this message translates to:
  /// **'Add Skill'**
  String get addSkill;

  /// No description provided for @submitSkills.
  ///
  /// In en, this message translates to:
  /// **'Submit Skills'**
  String get submitSkills;

  /// No description provided for @trackYourProgress.
  ///
  /// In en, this message translates to:
  /// **'Your Progress'**
  String get trackYourProgress;

  /// No description provided for @trackLearningJourney.
  ///
  /// In en, this message translates to:
  /// **'Track your learning journey'**
  String get trackLearningJourney;

  /// No description provided for @skillGrowth.
  ///
  /// In en, this message translates to:
  /// **'Skill Growth'**
  String get skillGrowth;

  /// No description provided for @weeklyActivity.
  ///
  /// In en, this message translates to:
  /// **'Weekly Activity'**
  String get weeklyActivity;

  /// No description provided for @noActivityData.
  ///
  /// In en, this message translates to:
  /// **'No activity data available'**
  String get noActivityData;

  /// No description provided for @completedCourses.
  ///
  /// In en, this message translates to:
  /// **'Completed Courses'**
  String get completedCourses;

  /// No description provided for @noCompletedCourses.
  ///
  /// In en, this message translates to:
  /// **'No completed courses yet'**
  String get noCompletedCourses;

  /// No description provided for @notifications.
  ///
  /// In en, this message translates to:
  /// **'Notifications'**
  String get notifications;

  /// No description provided for @newNotificationsCount.
  ///
  /// In en, this message translates to:
  /// **'{count} new notifications'**
  String newNotificationsCount(int count);

  /// No description provided for @markAllRead.
  ///
  /// In en, this message translates to:
  /// **'Mark all read'**
  String get markAllRead;

  /// No description provided for @noNotificationsYet.
  ///
  /// In en, this message translates to:
  /// **'No notifications yet'**
  String get noNotificationsYet;

  /// No description provided for @notificationsEmptyDesc.
  ///
  /// In en, this message translates to:
  /// **'You\'ll see notifications here when you have updates'**
  String get notificationsEmptyDesc;

  /// No description provided for @notificationDeleted.
  ///
  /// In en, this message translates to:
  /// **'Notification deleted'**
  String get notificationDeleted;

  /// No description provided for @failedToLoadNotifications.
  ///
  /// In en, this message translates to:
  /// **'Failed to load notifications'**
  String get failedToLoadNotifications;

  /// No description provided for @failedToMarkAsRead.
  ///
  /// In en, this message translates to:
  /// **'Failed to mark as read'**
  String get failedToMarkAsRead;

  /// No description provided for @failedToDeleteNotification.
  ///
  /// In en, this message translates to:
  /// **'Failed to delete notification'**
  String get failedToDeleteNotification;

  /// No description provided for @allMarkedAsRead.
  ///
  /// In en, this message translates to:
  /// **'All notifications marked as read'**
  String get allMarkedAsRead;

  /// No description provided for @failedToMarkAllRead.
  ///
  /// In en, this message translates to:
  /// **'Failed to mark all as read'**
  String get failedToMarkAllRead;

  /// No description provided for @justNow.
  ///
  /// In en, this message translates to:
  /// **'Just now'**
  String get justNow;

  /// No description provided for @minutesAgo.
  ///
  /// In en, this message translates to:
  /// **'{count} minutes ago'**
  String minutesAgo(int count);

  /// No description provided for @hoursAgo.
  ///
  /// In en, this message translates to:
  /// **'{count} hours ago'**
  String hoursAgo(int count);

  /// No description provided for @yesterday.
  ///
  /// In en, this message translates to:
  /// **'Yesterday'**
  String get yesterday;

  /// No description provided for @daysAgo.
  ///
  /// In en, this message translates to:
  /// **'{count} days ago'**
  String daysAgo(int count);

  /// No description provided for @unreadNotifications.
  ///
  /// In en, this message translates to:
  /// **'You have {count} unread notifications'**
  String unreadNotifications(int count);

  /// No description provided for @stayUpdated.
  ///
  /// In en, this message translates to:
  /// **'Stay updated with your progress'**
  String get stayUpdated;

  /// No description provided for @settings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings;

  /// No description provided for @manageAccount.
  ///
  /// In en, this message translates to:
  /// **'Manage your account'**
  String get manageAccount;

  /// No description provided for @editProfile.
  ///
  /// In en, this message translates to:
  /// **'Edit Profile'**
  String get editProfile;

  /// No description provided for @updateYourInfo.
  ///
  /// In en, this message translates to:
  /// **'Update your information'**
  String get updateYourInfo;

  /// No description provided for @notificationSettings.
  ///
  /// In en, this message translates to:
  /// **'Notifications'**
  String get notificationSettings;

  /// No description provided for @manageAlerts.
  ///
  /// In en, this message translates to:
  /// **'Manage your alerts'**
  String get manageAlerts;

  /// No description provided for @privacySecurity.
  ///
  /// In en, this message translates to:
  /// **'Privacy & Security'**
  String get privacySecurity;

  /// No description provided for @keepDataSafe.
  ///
  /// In en, this message translates to:
  /// **'Keep your data safe'**
  String get keepDataSafe;

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// No description provided for @arabic.
  ///
  /// In en, this message translates to:
  /// **'Arabic'**
  String get arabic;

  /// No description provided for @english.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get english;

  /// No description provided for @helpSupport.
  ///
  /// In en, this message translates to:
  /// **'Help & Support'**
  String get helpSupport;

  /// No description provided for @getAssistance.
  ///
  /// In en, this message translates to:
  /// **'Get assistance'**
  String get getAssistance;

  /// No description provided for @loading.
  ///
  /// In en, this message translates to:
  /// **'Loading...'**
  String get loading;

  /// No description provided for @failedToLoadProfile.
  ///
  /// In en, this message translates to:
  /// **'Failed to load profile'**
  String get failedToLoadProfile;

  /// No description provided for @phone.
  ///
  /// In en, this message translates to:
  /// **'Phone'**
  String get phone;

  /// No description provided for @bio.
  ///
  /// In en, this message translates to:
  /// **'Bio'**
  String get bio;

  /// No description provided for @saveChanges.
  ///
  /// In en, this message translates to:
  /// **'Save Changes'**
  String get saveChanges;

  /// No description provided for @profileUpdatedSuccess.
  ///
  /// In en, this message translates to:
  /// **'Profile updated successfully'**
  String get profileUpdatedSuccess;

  /// No description provided for @failedToUpdateProfile.
  ///
  /// In en, this message translates to:
  /// **'Failed to update profile: {error}'**
  String failedToUpdateProfile(String error);

  /// No description provided for @changePassword.
  ///
  /// In en, this message translates to:
  /// **'Change Password'**
  String get changePassword;

  /// No description provided for @passwordMinLength8.
  ///
  /// In en, this message translates to:
  /// **'Your password must be at least 8 characters long'**
  String get passwordMinLength8;

  /// No description provided for @currentPassword.
  ///
  /// In en, this message translates to:
  /// **'Current Password'**
  String get currentPassword;

  /// No description provided for @enterCurrentPassword.
  ///
  /// In en, this message translates to:
  /// **'Enter current password'**
  String get enterCurrentPassword;

  /// No description provided for @newPassword.
  ///
  /// In en, this message translates to:
  /// **'New Password'**
  String get newPassword;

  /// No description provided for @enterNewPassword.
  ///
  /// In en, this message translates to:
  /// **'Enter new password'**
  String get enterNewPassword;

  /// No description provided for @confirmNewPassword.
  ///
  /// In en, this message translates to:
  /// **'Confirm New Password'**
  String get confirmNewPassword;

  /// No description provided for @confirmNewPasswordHint.
  ///
  /// In en, this message translates to:
  /// **'Confirm new password'**
  String get confirmNewPasswordHint;

  /// No description provided for @pleaseEnterCurrentPassword.
  ///
  /// In en, this message translates to:
  /// **'Please enter your current password'**
  String get pleaseEnterCurrentPassword;

  /// No description provided for @pleaseEnterNewPassword.
  ///
  /// In en, this message translates to:
  /// **'Please enter a new password'**
  String get pleaseEnterNewPassword;

  /// No description provided for @passwordMin8Chars.
  ///
  /// In en, this message translates to:
  /// **'Password must be at least 8 characters'**
  String get passwordMin8Chars;

  /// No description provided for @newPasswordMustDiffer.
  ///
  /// In en, this message translates to:
  /// **'New password must be different from current'**
  String get newPasswordMustDiffer;

  /// No description provided for @pleaseConfirmNewPassword.
  ///
  /// In en, this message translates to:
  /// **'Please confirm your new password'**
  String get pleaseConfirmNewPassword;

  /// No description provided for @passwordChangedSuccess.
  ///
  /// In en, this message translates to:
  /// **'Password changed successfully!'**
  String get passwordChangedSuccess;

  /// No description provided for @failedToChangePassword.
  ///
  /// In en, this message translates to:
  /// **'Failed to change password: {error}'**
  String failedToChangePassword(String error);

  /// No description provided for @weak.
  ///
  /// In en, this message translates to:
  /// **'Weak'**
  String get weak;

  /// No description provided for @fair.
  ///
  /// In en, this message translates to:
  /// **'Fair'**
  String get fair;

  /// No description provided for @good.
  ///
  /// In en, this message translates to:
  /// **'Good'**
  String get good;

  /// No description provided for @strong.
  ///
  /// In en, this message translates to:
  /// **'Strong'**
  String get strong;

  /// No description provided for @atLeast8Chars.
  ///
  /// In en, this message translates to:
  /// **'At least 8 characters'**
  String get atLeast8Chars;

  /// No description provided for @containsUppercase.
  ///
  /// In en, this message translates to:
  /// **'Contains uppercase letter'**
  String get containsUppercase;

  /// No description provided for @containsLowercase.
  ///
  /// In en, this message translates to:
  /// **'Contains lowercase letter'**
  String get containsLowercase;

  /// No description provided for @containsNumber.
  ///
  /// In en, this message translates to:
  /// **'Contains number'**
  String get containsNumber;

  /// No description provided for @selectLanguage.
  ///
  /// In en, this message translates to:
  /// **'Select Language'**
  String get selectLanguage;

  /// No description provided for @languageUpdatedSuccess.
  ///
  /// In en, this message translates to:
  /// **'Language updated successfully'**
  String get languageUpdatedSuccess;

  /// No description provided for @notificationSettingsTitle.
  ///
  /// In en, this message translates to:
  /// **'Notification Settings'**
  String get notificationSettingsTitle;

  /// No description provided for @general.
  ///
  /// In en, this message translates to:
  /// **'General'**
  String get general;

  /// No description provided for @pushNotifications.
  ///
  /// In en, this message translates to:
  /// **'Push Notifications'**
  String get pushNotifications;

  /// No description provided for @receivePushNotifications.
  ///
  /// In en, this message translates to:
  /// **'Receive push notifications'**
  String get receivePushNotifications;

  /// No description provided for @emailNotifications.
  ///
  /// In en, this message translates to:
  /// **'Email Notifications'**
  String get emailNotifications;

  /// No description provided for @receiveEmailUpdates.
  ///
  /// In en, this message translates to:
  /// **'Receive email updates'**
  String get receiveEmailUpdates;

  /// No description provided for @notificationTypes.
  ///
  /// In en, this message translates to:
  /// **'Notification Types'**
  String get notificationTypes;

  /// No description provided for @courseUpdates.
  ///
  /// In en, this message translates to:
  /// **'Course Updates'**
  String get courseUpdates;

  /// No description provided for @newCoursesContent.
  ///
  /// In en, this message translates to:
  /// **'New courses and content'**
  String get newCoursesContent;

  /// No description provided for @progressReports.
  ///
  /// In en, this message translates to:
  /// **'Progress Reports'**
  String get progressReports;

  /// No description provided for @weeklyProgressSummary.
  ///
  /// In en, this message translates to:
  /// **'Weekly progress summary'**
  String get weeklyProgressSummary;

  /// No description provided for @achievements.
  ///
  /// In en, this message translates to:
  /// **'Achievements'**
  String get achievements;

  /// No description provided for @badgesAndRewards.
  ///
  /// In en, this message translates to:
  /// **'Badges and rewards'**
  String get badgesAndRewards;

  /// No description provided for @recommendations.
  ///
  /// In en, this message translates to:
  /// **'Recommendations'**
  String get recommendations;

  /// No description provided for @personalizedSuggestions.
  ///
  /// In en, this message translates to:
  /// **'Personalized suggestions'**
  String get personalizedSuggestions;

  /// No description provided for @security.
  ///
  /// In en, this message translates to:
  /// **'Security'**
  String get security;

  /// No description provided for @updateYourPassword.
  ///
  /// In en, this message translates to:
  /// **'Update your password'**
  String get updateYourPassword;

  /// No description provided for @twoFactorAuth.
  ///
  /// In en, this message translates to:
  /// **'Two-Factor Authentication'**
  String get twoFactorAuth;

  /// No description provided for @extraSecurityLayer.
  ///
  /// In en, this message translates to:
  /// **'Extra security layer'**
  String get extraSecurityLayer;

  /// No description provided for @biometricLogin.
  ///
  /// In en, this message translates to:
  /// **'Biometric Login'**
  String get biometricLogin;

  /// No description provided for @useFingerprintOrFace.
  ///
  /// In en, this message translates to:
  /// **'Use fingerprint or face'**
  String get useFingerprintOrFace;

  /// No description provided for @privacy.
  ///
  /// In en, this message translates to:
  /// **'Privacy'**
  String get privacy;

  /// No description provided for @profileVisibility.
  ///
  /// In en, this message translates to:
  /// **'Profile Visibility'**
  String get profileVisibility;

  /// No description provided for @whoCanSeeProfile.
  ///
  /// In en, this message translates to:
  /// **'Who can see your profile'**
  String get whoCanSeeProfile;

  /// No description provided for @profileVisibilityComingSoon.
  ///
  /// In en, this message translates to:
  /// **'Profile visibility settings coming soon.'**
  String get profileVisibilityComingSoon;

  /// No description provided for @downloadMyData.
  ///
  /// In en, this message translates to:
  /// **'Download My Data'**
  String get downloadMyData;

  /// No description provided for @getCopyOfData.
  ///
  /// In en, this message translates to:
  /// **'Get a copy of your data'**
  String get getCopyOfData;

  /// No description provided for @dataDownloadComingSoon.
  ///
  /// In en, this message translates to:
  /// **'Data download feature coming soon.'**
  String get dataDownloadComingSoon;

  /// No description provided for @account.
  ///
  /// In en, this message translates to:
  /// **'Account'**
  String get account;

  /// No description provided for @logout.
  ///
  /// In en, this message translates to:
  /// **'Logout'**
  String get logout;

  /// No description provided for @signOutOfAccount.
  ///
  /// In en, this message translates to:
  /// **'Sign out of your account'**
  String get signOutOfAccount;

  /// No description provided for @logoutConfirmation.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to logout?'**
  String get logoutConfirmation;

  /// No description provided for @deleteAccount.
  ///
  /// In en, this message translates to:
  /// **'Delete Account'**
  String get deleteAccount;

  /// No description provided for @permanentlyDeleteAccount.
  ///
  /// In en, this message translates to:
  /// **'Permanently delete account'**
  String get permanentlyDeleteAccount;

  /// No description provided for @deleteAccountWarning.
  ///
  /// In en, this message translates to:
  /// **'This action cannot be undone. All your data will be permanently deleted.'**
  String get deleteAccountWarning;

  /// No description provided for @accountDeletionNotAvailable.
  ///
  /// In en, this message translates to:
  /// **'Account deletion is not yet available.'**
  String get accountDeletionNotAvailable;

  /// No description provided for @getHelp.
  ///
  /// In en, this message translates to:
  /// **'Get Help'**
  String get getHelp;

  /// No description provided for @faqs.
  ///
  /// In en, this message translates to:
  /// **'FAQs'**
  String get faqs;

  /// No description provided for @frequentlyAskedQuestions.
  ///
  /// In en, this message translates to:
  /// **'Frequently asked questions'**
  String get frequentlyAskedQuestions;

  /// No description provided for @liveChat.
  ///
  /// In en, this message translates to:
  /// **'Live Chat'**
  String get liveChat;

  /// No description provided for @chatWithSupport.
  ///
  /// In en, this message translates to:
  /// **'Chat with support team'**
  String get chatWithSupport;

  /// No description provided for @emailSupport.
  ///
  /// In en, this message translates to:
  /// **'Email Support'**
  String get emailSupport;

  /// No description provided for @resources.
  ///
  /// In en, this message translates to:
  /// **'Resources'**
  String get resources;

  /// No description provided for @videoTutorials.
  ///
  /// In en, this message translates to:
  /// **'Video Tutorials'**
  String get videoTutorials;

  /// No description provided for @learnHowToUse.
  ///
  /// In en, this message translates to:
  /// **'Learn how to use Viora'**
  String get learnHowToUse;

  /// No description provided for @userGuide.
  ///
  /// In en, this message translates to:
  /// **'User Guide'**
  String get userGuide;

  /// No description provided for @completeDocumentation.
  ///
  /// In en, this message translates to:
  /// **'Complete documentation'**
  String get completeDocumentation;

  /// No description provided for @about.
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get about;

  /// No description provided for @aboutViora.
  ///
  /// In en, this message translates to:
  /// **'About Viora'**
  String get aboutViora;

  /// No description provided for @versionInfo.
  ///
  /// In en, this message translates to:
  /// **'Version 1.0.0'**
  String get versionInfo;

  /// No description provided for @termsOfService.
  ///
  /// In en, this message translates to:
  /// **'Terms of Service'**
  String get termsOfService;

  /// No description provided for @readOurTerms.
  ///
  /// In en, this message translates to:
  /// **'Read our terms'**
  String get readOurTerms;

  /// No description provided for @privacyPolicy.
  ///
  /// In en, this message translates to:
  /// **'Privacy Policy'**
  String get privacyPolicy;

  /// No description provided for @howWeProtectData.
  ///
  /// In en, this message translates to:
  /// **'How we protect your data'**
  String get howWeProtectData;

  /// No description provided for @comingSoon.
  ///
  /// In en, this message translates to:
  /// **'{feature} coming soon.'**
  String comingSoon(String feature);

  /// No description provided for @aiAssistant.
  ///
  /// In en, this message translates to:
  /// **'AI Assistant'**
  String get aiAssistant;

  /// No description provided for @askMeAnything.
  ///
  /// In en, this message translates to:
  /// **'Ask me anything about your career...'**
  String get askMeAnything;

  /// No description provided for @typeMessage.
  ///
  /// In en, this message translates to:
  /// **'Type your message...'**
  String get typeMessage;

  /// No description provided for @errorNetwork.
  ///
  /// In en, this message translates to:
  /// **'Network error occurred'**
  String get errorNetwork;

  /// No description provided for @errorServer.
  ///
  /// In en, this message translates to:
  /// **'Server error occurred'**
  String get errorServer;

  /// No description provided for @errorUnauthorized.
  ///
  /// In en, this message translates to:
  /// **'Session expired. Please login again'**
  String get errorUnauthorized;

  /// No description provided for @errorTimeout.
  ///
  /// In en, this message translates to:
  /// **'Request timed out'**
  String get errorTimeout;

  /// No description provided for @errorUnknown.
  ///
  /// In en, this message translates to:
  /// **'An unexpected error occurred'**
  String get errorUnknown;

  /// No description provided for @languageUpdated.
  ///
  /// In en, this message translates to:
  /// **'Language updated successfully'**
  String get languageUpdated;

  /// No description provided for @navHome.
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get navHome;

  /// No description provided for @navProgress.
  ///
  /// In en, this message translates to:
  /// **'Progress'**
  String get navProgress;

  /// No description provided for @navAssistant.
  ///
  /// In en, this message translates to:
  /// **'Assistant'**
  String get navAssistant;

  /// No description provided for @navProfile.
  ///
  /// In en, this message translates to:
  /// **'Profile'**
  String get navProfile;

  /// No description provided for @smartAssistantTitle.
  ///
  /// In en, this message translates to:
  /// **'Smart Assistant'**
  String get smartAssistantTitle;

  /// No description provided for @alwaysHereToHelp.
  ///
  /// In en, this message translates to:
  /// **'Always here to help'**
  String get alwaysHereToHelp;

  /// No description provided for @quickActions.
  ///
  /// In en, this message translates to:
  /// **'Quick actions:'**
  String get quickActions;

  /// No description provided for @analyzeCV.
  ///
  /// In en, this message translates to:
  /// **'Analyze CV'**
  String get analyzeCV;

  /// No description provided for @helpAnalyzeCV.
  ///
  /// In en, this message translates to:
  /// **'Help me analyze my CV'**
  String get helpAnalyzeCV;

  /// No description provided for @careerAdvice.
  ///
  /// In en, this message translates to:
  /// **'Career Advice'**
  String get careerAdvice;

  /// No description provided for @giveCareerAdvice.
  ///
  /// In en, this message translates to:
  /// **'Give me career advice based on my skills'**
  String get giveCareerAdvice;

  /// No description provided for @findCourses.
  ///
  /// In en, this message translates to:
  /// **'Find Courses'**
  String get findCourses;

  /// No description provided for @recommendCourses.
  ///
  /// In en, this message translates to:
  /// **'Recommend courses to improve my skills'**
  String get recommendCourses;

  /// No description provided for @hiHowCanIHelp.
  ///
  /// In en, this message translates to:
  /// **'Hi! How can I assist you today?'**
  String get hiHowCanIHelp;

  /// No description provided for @askAboutCareer.
  ///
  /// In en, this message translates to:
  /// **'Ask me anything about your career development'**
  String get askAboutCareer;

  /// No description provided for @failedToLoadCourseDetails.
  ///
  /// In en, this message translates to:
  /// **'Failed to load course'**
  String get failedToLoadCourseDetails;

  /// No description provided for @courseNotFoundMsg.
  ///
  /// In en, this message translates to:
  /// **'Course not found'**
  String get courseNotFoundMsg;

  /// No description provided for @enrolledLabel.
  ///
  /// In en, this message translates to:
  /// **'Enrolled'**
  String get enrolledLabel;

  /// No description provided for @completedLabel.
  ///
  /// In en, this message translates to:
  /// **'Completed'**
  String get completedLabel;

  /// No description provided for @notEnrolledLabel.
  ///
  /// In en, this message translates to:
  /// **'Not enrolled'**
  String get notEnrolledLabel;

  /// No description provided for @courseProgressTitle.
  ///
  /// In en, this message translates to:
  /// **'Course Progress'**
  String get courseProgressTitle;

  /// No description provided for @courseDetailsTitle.
  ///
  /// In en, this message translates to:
  /// **'Course Details'**
  String get courseDetailsTitle;

  /// No description provided for @titleLabel.
  ///
  /// In en, this message translates to:
  /// **'Title'**
  String get titleLabel;

  /// No description provided for @categoryLabel.
  ///
  /// In en, this message translates to:
  /// **'Category'**
  String get categoryLabel;

  /// No description provided for @platformLabel.
  ///
  /// In en, this message translates to:
  /// **'Platform'**
  String get platformLabel;

  /// No description provided for @statusLabel.
  ///
  /// In en, this message translates to:
  /// **'Status'**
  String get statusLabel;

  /// No description provided for @markAsCompletedBtn.
  ///
  /// In en, this message translates to:
  /// **'Mark as Completed'**
  String get markAsCompletedBtn;

  /// No description provided for @deleteCourseBtn.
  ///
  /// In en, this message translates to:
  /// **'Delete Course'**
  String get deleteCourseBtn;

  /// No description provided for @deleteBtn.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get deleteBtn;

  /// No description provided for @notStartedStatus.
  ///
  /// In en, this message translates to:
  /// **'Not Started'**
  String get notStartedStatus;

  /// No description provided for @inProgressStatus.
  ///
  /// In en, this message translates to:
  /// **'In Progress'**
  String get inProgressStatus;

  /// No description provided for @completedStatus.
  ///
  /// In en, this message translates to:
  /// **'Completed'**
  String get completedStatus;

  /// No description provided for @areYouSureDeleteCourse.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete \"{title}\"?'**
  String areYouSureDeleteCourse(String title);

  /// No description provided for @failedToLoadRoadmap.
  ///
  /// In en, this message translates to:
  /// **'Failed to load roadmap'**
  String get failedToLoadRoadmap;

  /// No description provided for @noRoadmapAvailable.
  ///
  /// In en, this message translates to:
  /// **'No roadmap available'**
  String get noRoadmapAvailable;

  /// No description provided for @completeSkillsFirst.
  ///
  /// In en, this message translates to:
  /// **'Complete your skills analysis first'**
  String get completeSkillsFirst;

  /// No description provided for @learningRoadmap.
  ///
  /// In en, this message translates to:
  /// **'Learning Roadmap'**
  String get learningRoadmap;

  /// No description provided for @personalizedPath.
  ///
  /// In en, this message translates to:
  /// **'Your personalized learning path'**
  String get personalizedPath;

  /// No description provided for @overallProgress.
  ///
  /// In en, this message translates to:
  /// **'Overall Progress'**
  String get overallProgress;

  /// No description provided for @phasesProgress.
  ///
  /// In en, this message translates to:
  /// **'{completed} of {total} phases'**
  String phasesProgress(int completed, int total);

  /// No description provided for @learningPhases.
  ///
  /// In en, this message translates to:
  /// **'Learning Phases'**
  String get learningPhases;

  /// No description provided for @duration.
  ///
  /// In en, this message translates to:
  /// **'Duration: {value}'**
  String duration(String value);

  /// No description provided for @topicsCount.
  ///
  /// In en, this message translates to:
  /// **'{count} topics'**
  String topicsCount(int count);

  /// No description provided for @recommendedResources.
  ///
  /// In en, this message translates to:
  /// **'Recommended Resources:'**
  String get recommendedResources;

  /// No description provided for @skillAnalysisTitle.
  ///
  /// In en, this message translates to:
  /// **'Skill Analysis'**
  String get skillAnalysisTitle;

  /// No description provided for @orText.
  ///
  /// In en, this message translates to:
  /// **'Or'**
  String get orText;

  /// No description provided for @uploadResume.
  ///
  /// In en, this message translates to:
  /// **'Upload Resume'**
  String get uploadResume;

  /// No description provided for @resumeSelected.
  ///
  /// In en, this message translates to:
  /// **'Resume Selected'**
  String get resumeSelected;

  /// No description provided for @pdfDocDocx.
  ///
  /// In en, this message translates to:
  /// **'PDF, DOC, or DOCX'**
  String get pdfDocDocx;

  /// No description provided for @removeFile.
  ///
  /// In en, this message translates to:
  /// **'Remove file'**
  String get removeFile;

  /// No description provided for @orTypeSkills.
  ///
  /// In en, this message translates to:
  /// **'Or type your skills'**
  String get orTypeSkills;

  /// No description provided for @skillsHintText.
  ///
  /// In en, this message translates to:
  /// **'e.g., JavaScript, React, TypeScript...'**
  String get skillsHintText;

  /// No description provided for @analyzeNow.
  ///
  /// In en, this message translates to:
  /// **'Analyze Now'**
  String get analyzeNow;

  /// No description provided for @errorSelectingFile.
  ///
  /// In en, this message translates to:
  /// **'Error selecting file: {error}'**
  String errorSelectingFile(String error);

  /// No description provided for @pleaseUploadOrEnter.
  ///
  /// In en, this message translates to:
  /// **'Please upload a resume or enter your skills manually'**
  String get pleaseUploadOrEnter;

  /// No description provided for @analysisCompletedSuccess.
  ///
  /// In en, this message translates to:
  /// **'Analysis completed successfully!'**
  String get analysisCompletedSuccess;

  /// No description provided for @analyzingResume.
  ///
  /// In en, this message translates to:
  /// **'Analyzing your resume...'**
  String get analyzingResume;

  /// No description provided for @mayTakeMoments.
  ///
  /// In en, this message translates to:
  /// **'This may take a few moments'**
  String get mayTakeMoments;

  /// No description provided for @strongSkills.
  ///
  /// In en, this message translates to:
  /// **'Strong Skills'**
  String get strongSkills;

  /// No description provided for @skillsToDevelop.
  ///
  /// In en, this message translates to:
  /// **'Skills to Develop'**
  String get skillsToDevelop;

  /// No description provided for @predictedCareer.
  ///
  /// In en, this message translates to:
  /// **'Predicted Career'**
  String get predictedCareer;

  /// No description provided for @levelLabel.
  ///
  /// In en, this message translates to:
  /// **'📊 Level: {level}'**
  String levelLabel(String level);

  /// No description provided for @readyToCreatePath.
  ///
  /// In en, this message translates to:
  /// **'Ready to Create Your Learning Path?'**
  String get readyToCreatePath;

  /// No description provided for @generatePersonalizedRoadmap.
  ///
  /// In en, this message translates to:
  /// **'Generate a personalized roadmap based on your skills analysis'**
  String get generatePersonalizedRoadmap;

  /// No description provided for @generateLearningRoadmap.
  ///
  /// In en, this message translates to:
  /// **'Generate Learning Roadmap →'**
  String get generateLearningRoadmap;

  /// No description provided for @roadmapGenerated.
  ///
  /// In en, this message translates to:
  /// **'🎉 Roadmap generated! Check Progress tab'**
  String get roadmapGenerated;

  /// No description provided for @analyzingText.
  ///
  /// In en, this message translates to:
  /// **'Analyzing...'**
  String get analyzingText;

  /// No description provided for @careerDirection.
  ///
  /// In en, this message translates to:
  /// **'Career Direction'**
  String get careerDirection;

  /// No description provided for @jobOpportunities.
  ///
  /// In en, this message translates to:
  /// **'Job Opportunities'**
  String get jobOpportunities;

  /// No description provided for @basedOnProfile.
  ///
  /// In en, this message translates to:
  /// **'Based on your profile:'**
  String get basedOnProfile;

  /// No description provided for @recommendationsTitle.
  ///
  /// In en, this message translates to:
  /// **'Recommendations'**
  String get recommendationsTitle;

  /// No description provided for @languageChangedTo.
  ///
  /// In en, this message translates to:
  /// **'Language changed to {name}'**
  String languageChangedTo(String name);

  /// No description provided for @failedToUpdateLanguage.
  ///
  /// In en, this message translates to:
  /// **'Failed to update language: {error}'**
  String failedToUpdateLanguage(String error);

  /// No description provided for @selectLanguageTitle.
  ///
  /// In en, this message translates to:
  /// **'Select Language'**
  String get selectLanguageTitle;

  /// No description provided for @languageTitle.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get languageTitle;

  /// No description provided for @dayMon.
  ///
  /// In en, this message translates to:
  /// **'Mon'**
  String get dayMon;

  /// No description provided for @dayTue.
  ///
  /// In en, this message translates to:
  /// **'Tue'**
  String get dayTue;

  /// No description provided for @dayWed.
  ///
  /// In en, this message translates to:
  /// **'Wed'**
  String get dayWed;

  /// No description provided for @dayThu.
  ///
  /// In en, this message translates to:
  /// **'Thu'**
  String get dayThu;

  /// No description provided for @dayFri.
  ///
  /// In en, this message translates to:
  /// **'Fri'**
  String get dayFri;

  /// No description provided for @daySat.
  ///
  /// In en, this message translates to:
  /// **'Sat'**
  String get daySat;

  /// No description provided for @daySun.
  ///
  /// In en, this message translates to:
  /// **'Sun'**
  String get daySun;

  /// No description provided for @startJourneyTitle.
  ///
  /// In en, this message translates to:
  /// **'Start Your Career Journey!'**
  String get startJourneyTitle;

  /// No description provided for @startJourneyDesc.
  ///
  /// In en, this message translates to:
  /// **'Upload your CV to discover your skills and get a personalized learning path.'**
  String get startJourneyDesc;

  /// No description provided for @analyzeMyCV.
  ///
  /// In en, this message translates to:
  /// **'Analyze My CV →'**
  String get analyzeMyCV;

  /// No description provided for @roadmapReadyTitle.
  ///
  /// In en, this message translates to:
  /// **'Your Learning Path is Ready!'**
  String get roadmapReadyTitle;

  /// No description provided for @roadmapReadyDesc.
  ///
  /// In en, this message translates to:
  /// **'View your personalized roadmap and start learning.'**
  String get roadmapReadyDesc;

  /// No description provided for @viewRoadmap.
  ///
  /// In en, this message translates to:
  /// **'View Roadmap →'**
  String get viewRoadmap;

  /// No description provided for @newAnalysis.
  ///
  /// In en, this message translates to:
  /// **'New Analysis'**
  String get newAnalysis;

  /// No description provided for @roadmapStepsProgress.
  ///
  /// In en, this message translates to:
  /// **'{completed}/{total} steps'**
  String roadmapStepsProgress(Object completed, Object total);

  /// No description provided for @coursesProgress.
  ///
  /// In en, this message translates to:
  /// **'{completed}/{total} courses'**
  String coursesProgress(Object completed, Object total);

  /// No description provided for @analyzeFirst.
  ///
  /// In en, this message translates to:
  /// **'Analyze your CV first to get a personalized learning path.'**
  String get analyzeFirst;

  /// No description provided for @goToAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Go to Analysis'**
  String get goToAnalysis;

  /// No description provided for @autoGeneratingRoadmap.
  ///
  /// In en, this message translates to:
  /// **'Generating your learning path...'**
  String get autoGeneratingRoadmap;

  /// No description provided for @navAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Analysis Skills'**
  String get navAnalysis;

  /// No description provided for @navRoadmap.
  ///
  /// In en, this message translates to:
  /// **'Roadmap'**
  String get navRoadmap;

  /// No description provided for @navAdvisor.
  ///
  /// In en, this message translates to:
  /// **'Advisor'**
  String get navAdvisor;

  /// No description provided for @resumeQuality.
  ///
  /// In en, this message translates to:
  /// **'Resume Quality'**
  String get resumeQuality;

  /// No description provided for @excellent.
  ///
  /// In en, this message translates to:
  /// **'Excellent'**
  String get excellent;

  /// No description provided for @acceptable.
  ///
  /// In en, this message translates to:
  /// **'Acceptable'**
  String get acceptable;

  /// No description provided for @wordsCount.
  ///
  /// In en, this message translates to:
  /// **'{count} words'**
  String wordsCount(int count);

  /// No description provided for @uploadingResume.
  ///
  /// In en, this message translates to:
  /// **'Uploading Your Resume...'**
  String get uploadingResume;

  /// No description provided for @extractingText.
  ///
  /// In en, this message translates to:
  /// **'Extracting Text...'**
  String get extractingText;

  /// No description provided for @aiSkillAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Analyzing Skills with AI...'**
  String get aiSkillAnalysis;

  /// No description provided for @careerMatching.
  ///
  /// In en, this message translates to:
  /// **'Matching Career Database...'**
  String get careerMatching;

  /// No description provided for @processing.
  ///
  /// In en, this message translates to:
  /// **'Processing...'**
  String get processing;

  /// No description provided for @uploadingDesc.
  ///
  /// In en, this message translates to:
  /// **'Securely uploading your CV to the server'**
  String get uploadingDesc;

  /// No description provided for @extractingDesc.
  ///
  /// In en, this message translates to:
  /// **'Reading and extracting content from your document'**
  String get extractingDesc;

  /// No description provided for @analyzingDesc.
  ///
  /// In en, this message translates to:
  /// **'Our AI model is identifying your skills and experience'**
  String get analyzingDesc;

  /// No description provided for @matchingDesc.
  ///
  /// In en, this message translates to:
  /// **'Comparing your profile with O*NET career standards'**
  String get matchingDesc;

  /// No description provided for @processingDesc.
  ///
  /// In en, this message translates to:
  /// **'Please wait while we process your resume'**
  String get processingDesc;

  /// No description provided for @usuallyTakes.
  ///
  /// In en, this message translates to:
  /// **'Usually takes 30–60 seconds'**
  String get usuallyTakes;

  /// No description provided for @uploadFile.
  ///
  /// In en, this message translates to:
  /// **'Upload File'**
  String get uploadFile;

  /// No description provided for @extractText.
  ///
  /// In en, this message translates to:
  /// **'Extract Text'**
  String get extractText;

  /// No description provided for @createLearningPath.
  ///
  /// In en, this message translates to:
  /// **'Create Learning Path'**
  String get createLearningPath;

  /// No description provided for @generatingPath.
  ///
  /// In en, this message translates to:
  /// **'Generating...'**
  String get generatingPath;

  /// No description provided for @profilePhotoUpdated.
  ///
  /// In en, this message translates to:
  /// **'Profile photo updated ✅'**
  String get profilePhotoUpdated;

  /// No description provided for @failedUploadPhoto.
  ///
  /// In en, this message translates to:
  /// **'Failed to upload photo'**
  String get failedUploadPhoto;

  /// No description provided for @showLess.
  ///
  /// In en, this message translates to:
  /// **'Show Less'**
  String get showLess;

  /// No description provided for @couldNotOpenLink.
  ///
  /// In en, this message translates to:
  /// **'Could not open this link'**
  String get couldNotOpenLink;

  /// No description provided for @showMoreResources.
  ///
  /// In en, this message translates to:
  /// **'Show {count} More Resources'**
  String showMoreResources(int count);

  /// No description provided for @showMore.
  ///
  /// In en, this message translates to:
  /// **'Show More'**
  String get showMore;

  /// No description provided for @reanalysisWarningTitle.
  ///
  /// In en, this message translates to:
  /// **'Re-analyze CV?'**
  String get reanalysisWarningTitle;

  /// No description provided for @reanalysisWarningBody.
  ///
  /// In en, this message translates to:
  /// **'This will archive your previous analysis and roadmap, and clear your chat history to focus on the new CV.'**
  String get reanalysisWarningBody;

  /// No description provided for @continueText.
  ///
  /// In en, this message translates to:
  /// **'Continue'**
  String get continueText;

  /// No description provided for @languages.
  ///
  /// In en, this message translates to:
  /// **'Languages'**
  String get languages;

  /// No description provided for @strengths.
  ///
  /// In en, this message translates to:
  /// **'Strengths'**
  String get strengths;

  /// No description provided for @fileTooLarge.
  ///
  /// In en, this message translates to:
  /// **'File too large ({size}MB). Maximum size is 10MB.'**
  String fileTooLarge(String size);

  /// No description provided for @tapToSelectFile.
  ///
  /// In en, this message translates to:
  /// **'Tap to select a file'**
  String get tapToSelectFile;

  /// No description provided for @pdfDocxUpTo10.
  ///
  /// In en, this message translates to:
  /// **'PDF, DOCX — up to 10MB'**
  String get pdfDocxUpTo10;

  /// No description provided for @newChat.
  ///
  /// In en, this message translates to:
  /// **'New Chat'**
  String get newChat;

  /// No description provided for @couldNotConnectAssistant.
  ///
  /// In en, this message translates to:
  /// **'Could not connect to assistant'**
  String get couldNotConnectAssistant;

  /// No description provided for @videos.
  ///
  /// In en, this message translates to:
  /// **'Videos'**
  String get videos;

  /// No description provided for @courses.
  ///
  /// In en, this message translates to:
  /// **'Courses'**
  String get courses;

  /// No description provided for @phaseCompleted.
  ///
  /// In en, this message translates to:
  /// **'Phase Completed!'**
  String get phaseCompleted;

  /// No description provided for @of_.
  ///
  /// In en, this message translates to:
  /// **'of'**
  String get of_;

  /// No description provided for @resourcesCompleted.
  ///
  /// In en, this message translates to:
  /// **'completed'**
  String get resourcesCompleted;

  /// No description provided for @resourcesTotal.
  ///
  /// In en, this message translates to:
  /// **'resources'**
  String get resourcesTotal;

  /// No description provided for @articles.
  ///
  /// In en, this message translates to:
  /// **'Articles'**
  String get articles;

  /// No description provided for @phases.
  ///
  /// In en, this message translates to:
  /// **'Phases'**
  String get phases;

  /// No description provided for @techSkills.
  ///
  /// In en, this message translates to:
  /// **'Technical Tools'**
  String get techSkills;

  /// No description provided for @hardSkills.
  ///
  /// In en, this message translates to:
  /// **'Core Competencies'**
  String get hardSkills;

  /// No description provided for @softSkills.
  ///
  /// In en, this message translates to:
  /// **'Professional Skills'**
  String get softSkills;

  /// No description provided for @errorArabicCV.
  ///
  /// In en, this message translates to:
  /// **'Please upload an English CV. Arabic CVs are not supported yet.'**
  String get errorArabicCV;

  /// No description provided for @errorInvalidCV.
  ///
  /// In en, this message translates to:
  /// **'The uploaded file doesn\'t appear to be a valid CV. Please check and try again.'**
  String get errorInvalidCV;

  /// No description provided for @errorImagePDF.
  ///
  /// In en, this message translates to:
  /// **'This PDF is image-based (scanned). Please upload a text-based PDF or DOCX.'**
  String get errorImagePDF;

  /// No description provided for @errorOldDocFormat.
  ///
  /// In en, this message translates to:
  /// **'Old .doc format is not supported. Please convert to .docx or .pdf.'**
  String get errorOldDocFormat;

  /// No description provided for @errorUnsupportedFormat.
  ///
  /// In en, this message translates to:
  /// **'Unsupported file format. Please use PDF or DOCX.'**
  String get errorUnsupportedFormat;

  /// No description provided for @errorQuotaExceeded.
  ///
  /// In en, this message translates to:
  /// **'Service temporarily unavailable due to high demand. Please try again later.'**
  String get errorQuotaExceeded;

  /// No description provided for @errorFileTooLarge.
  ///
  /// In en, this message translates to:
  /// **'File is too large. Maximum size is 10MB.'**
  String get errorFileTooLarge;

  /// No description provided for @errorConnectionTimeout.
  ///
  /// In en, this message translates to:
  /// **'Connection timed out. Please check your internet connection.'**
  String get errorConnectionTimeout;

  /// No description provided for @errorNoConnection.
  ///
  /// In en, this message translates to:
  /// **'Could not connect to server. Please check your internet connection.'**
  String get errorNoConnection;

  /// No description provided for @errorAnalysisTimeout.
  ///
  /// In en, this message translates to:
  /// **'Analysis took too long. Please try again.'**
  String get errorAnalysisTimeout;

  /// No description provided for @errorGeneric.
  ///
  /// In en, this message translates to:
  /// **'An error occurred. Please try again.'**
  String get errorGeneric;

  /// No description provided for @phoneNumber.
  ///
  /// In en, this message translates to:
  /// **'Phone Number'**
  String get phoneNumber;

  /// No description provided for @bioHint.
  ///
  /// In en, this message translates to:
  /// **'Tell us about yourself...'**
  String get bioHint;

  /// No description provided for @memberSince.
  ///
  /// In en, this message translates to:
  /// **'Member since'**
  String get memberSince;

  /// No description provided for @topics.
  ///
  /// In en, this message translates to:
  /// **'Topics'**
  String get topics;

  /// No description provided for @yourJourney.
  ///
  /// In en, this message translates to:
  /// **'Your Journey'**
  String get yourJourney;

  /// No description provided for @cvAnalyzed.
  ///
  /// In en, this message translates to:
  /// **'CV Analyzed'**
  String get cvAnalyzed;

  /// No description provided for @roadmapReady.
  ///
  /// In en, this message translates to:
  /// **'Roadmap Generated'**
  String get roadmapReady;

  /// No description provided for @learningStarted.
  ///
  /// In en, this message translates to:
  /// **'Learning in Progress'**
  String get learningStarted;

  /// No description provided for @phaseNotFound.
  ///
  /// In en, this message translates to:
  /// **'Phase not found'**
  String get phaseNotFound;

  /// No description provided for @showAllCount.
  ///
  /// In en, this message translates to:
  /// **'Show all ({count})'**
  String showAllCount(int count);

  /// No description provided for @appCopyright.
  ///
  /// In en, this message translates to:
  /// **'© 2026 Viora'**
  String get appCopyright;

  /// No description provided for @appDescription.
  ///
  /// In en, this message translates to:
  /// **'AI-powered career development and skills analysis app'**
  String get appDescription;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['ar', 'en'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'ar':
      return AppLocalizationsAr();
    case 'en':
      return AppLocalizationsEn();
  }

  throw FlutterError(
      'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
