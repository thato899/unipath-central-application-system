# UniPath mobile app

Native Android and iOS student client built with Expo SDK 58 and React Native. It connects to the UniPath Django API and supports password + TOTP sign-in, course search across faculties, sample eligibility matching, applications to selected universities, offer acceptance/rejection, residence requests after acceptance, funding destination summaries, profile editing, data export, and account deletion.

The app keeps the bearer token in Expo SecureStore (Android Keystore-backed encrypted storage and iOS Keychain) and does not persist the profile or marks locally. The API stores only a hash of each mobile token. Tokens expire after eight hours and are revoked at sign-out. Use HTTPS for any non-local deployment and fictional information only.

## Prerequisites

- Node.js 22.13 or newer (required by this Expo SDK).
- The Django backend installed and migrated using the repository instructions.
- Expo Go or an Android/iOS simulator. For iOS native builds, a Mac with Xcode is required.

## Configure and run

Copy `.env.example` to `.env` and set `EXPO_PUBLIC_API_URL` to the backend address. Install dependencies and start Expo:

~~~powershell
Copy-Item .env.example .env
npm install
npm run start
~~~

The Expo SDK 58 toolchain requires Node.js 22.13 or newer.

Use `npm run android` or `npm run ios` to open the respective simulator when it is installed. Android emulator uses `http://10.0.2.2:8000` to reach the host machine. iOS simulator can use `http://127.0.0.1:8000`. For a phone on the same trusted development network, bind Django to the LAN and allow the host address:

~~~powershell
$env:ALLOWED_HOSTS="192.168.1.20,127.0.0.1,localhost"
python manage.py runserver 0.0.0.0:8000
~~~

Replace `192.168.1.20` with the development computer's LAN address and use that address for `EXPO_PUBLIC_API_URL`. For production, use an HTTPS API endpoint.

Create the account in the web version first, then enroll an authenticator app through the web 2FA setup. Sign in to the native app using that email, password, and six-digit code. The registration link opens the web account setup.

## Accessibility

Controls use native accessibility roles and labels for VoiceOver and TalkBack. The app provides text resizing, a high-contrast option, read-aloud support, and large touch targets. Course matching status is written as text, and application actions have descriptive labels.

The mobile app does not implement authenticator recovery, real university/NSFAS connections, push notifications, statement upload, or offline application storage. This is a prototype, not a POPIA compliance certification.

## Dependency audit note

The current npm audit reports high-severity advisories in transitive Expo/Metro build-tool dependencies. A compatible automatic fix was not available; npm's forced fix proposes downgrading Expo to an older major release. Recheck the Expo dependency tree for upstream patches before publishing a store build.
