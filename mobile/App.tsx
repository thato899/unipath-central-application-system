import { StatusBar } from 'expo-status-bar';
import * as SecureStore from 'expo-secure-store';
import * as Speech from 'expo-speech';
import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import {
  ActivityIndicator, Alert, Linking, Pressable, SafeAreaView, ScrollView, StyleSheet,
  Share, Switch, Text as NativeText, TextInput, View,
} from 'react-native';

const API = (process.env.EXPO_PUBLIC_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
const TOKEN_KEY = 'unipath.mobile.access-token';
const BASE_SUBJECTS = ['Home or First Additional Language', 'Mathematics', 'Life Orientation', '', '', '', ''];
type Profile = { name: string; email?: string; upgrading: boolean; marks: { aps: number; mathematics: number; english: number; subjects: Record<string, number> } };
type Course = { id: string; name?: string; short_name?: string; faculty: string; description?: string; careers?: string[]; match_count?: number };
type Match = { university: { id: string; name: string }; requirements: { aps: number; mathematics: number; english: number }; status: string };
type Application = { id: string; course_id: string; course_name: string; university_id: string; university_name: string; status: string; decision?: string | null };
type Residence = { application_id: string; university_name: string; preference: string; status: string };
const TextScale = createContext(1);

function Text(props: React.ComponentProps<typeof NativeText>) {
  const scale = useContext(TextScale);
  const flattened = StyleSheet.flatten(props.style);
  const fontSize = typeof flattened?.fontSize === 'number' ? flattened.fontSize * scale : undefined;
  return <NativeText {...props} style={[props.style, fontSize ? { fontSize } : null]} />;
}

function Button({ title, onPress, secondary = false, disabled = false, accessibilityLabel }: { title: string; onPress: () => void; secondary?: boolean; disabled?: boolean; accessibilityLabel?: string }) {
  return <Pressable accessibilityRole="button" accessibilityLabel={accessibilityLabel || title} onPress={onPress} disabled={disabled} style={({ pressed }) => [styles.button, secondary && styles.buttonSecondary, disabled && styles.disabled, pressed && !disabled && styles.pressed]}>
    <Text style={[styles.buttonText, secondary && styles.buttonSecondaryText]}>{title}</Text>
  </Pressable>;
}

function Field({ label, value, onChangeText, keyboardType, secureTextEntry, hint }: { label: string; value: string; onChangeText: (value: string) => void; keyboardType?: 'default' | 'email-address' | 'numeric'; secureTextEntry?: boolean; hint?: string }) {
  const scale = useContext(TextScale);
  return <View style={styles.fieldWrap}>
    <Text accessibilityRole="text" style={[styles.label, { fontSize: 15 * scale }]}>{label}</Text>
    <TextInput accessibilityLabel={label} accessibilityHint={hint} style={[styles.input, { fontSize: 16 * scale }]} value={value} onChangeText={onChangeText} keyboardType={keyboardType || 'default'} secureTextEntry={secureTextEntry} autoCapitalize={keyboardType === 'email-address' ? 'none' : 'sentences'} />
    {hint ? <Text style={styles.hint}>{hint}</Text> : null}
  </View>;
}

export default function App() {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [tab, setTab] = useState<'courses' | 'applications' | 'profile'>('courses');
  const [courses, setCourses] = useState<Course[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [residences, setResidences] = useState<Residence[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [accountEmail, setAccountEmail] = useState('');
  const [course, setCourse] = useState<Course | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [search, setSearch] = useState('');
  const [readScale, setReadScale] = useState(1);
  const [highContrast, setHighContrast] = useState(false);
  const [profileName, setProfileName] = useState('');
  const [aps, setAps] = useState('');
  const [math, setMath] = useState('');
  const [english, setEnglish] = useState('');
  const [subjectNames, setSubjectNames] = useState<string[]>(BASE_SUBJECTS);
  const [subjectScores, setSubjectScores] = useState<string[]>(['', '', '', '', '', '', '']);
  const [upgrading, setUpgrading] = useState(false);
  const [residenceTarget, setResidenceTarget] = useState('');
  const [residencePreference, setResidencePreference] = useState('On-campus residence');
  const [accommodationNeeds, setAccommodationNeeds] = useState('');
  const [fundingMessage, setFundingMessage] = useState('');
  const [deletePassword, setDeletePassword] = useState('');
  const [deleteOtp, setDeleteOtp] = useState('');

  const speak = (text: string) => Speech.speak(text, { language: 'en-ZA', rate: 0.92 });
  const api = useCallback(async (path: string, method = 'GET', body?: unknown) => {
    const response = await fetch(`${API}/api/${path}`, {
      method,
      headers: { Accept: 'application/json', ...(body ? { 'Content-Type': 'application/json' } : {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || `Request failed (${response.status}).`);
    return data;
  }, [token]);

  const loadData = useCallback(async () => {
    const [courseData, profileData, applicationData, residenceData] = await Promise.all([
      api('courses'), api('profile'), api('applications'), api('residence'),
    ]);
    setCourses(courseData.courses || []);
    setApplications(applicationData.applications || []);
    setResidences(residenceData.residence_applications || []);
    const next: Profile | null = profileData.profile;
    setAccountEmail(profileData.account_email || '');
    setProfile(next);
    if (next) {
      setProfileName(next.name || ''); setAps(String(next.marks?.aps ?? ''));
      setMath(String(next.marks?.mathematics ?? '')); setEnglish(String(next.marks?.english ?? ''));
      setUpgrading(Boolean(next.upgrading));
      const entries = Object.entries(next.marks?.subjects || {});
      setSubjectNames(Array.from({ length: 7 }, (_, index) => entries[index]?.[0] || ''));
      setSubjectScores(Array.from({ length: 7 }, (_, index) => entries[index] ? String(entries[index][1]) : ''));
    }
  }, [api]);

  useEffect(() => { SecureStore.getItemAsync(TOKEN_KEY).then((saved) => { if (saved) setToken(saved); }).catch(() => {}); }, []);
  useEffect(() => {
    if (!token) return;
    setBusy(true);
    loadData().then(() => setMessage('Your secure account is ready.')).catch((error) => {
      setMessage(error.message);
      if (error.message.includes('Sign in')) signOut();
    }).finally(() => setBusy(false));
  }, [token, loadData]);

  async function signIn() {
    setBusy(true); setMessage('');
    try {
      const response = await fetch(`${API}/api/mobile/login`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase(), password, otp_token: otp.trim() }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Sign-in failed.');
      await SecureStore.setItemAsync(TOKEN_KEY, data.access_token, { keychainAccessible: SecureStore.WHEN_UNLOCKED });
      setPassword(''); setOtp(''); setToken(data.access_token);
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Could not sign in. Check the API address and try again.'); }
    finally { setBusy(false); }
  }

  async function signOut() {
    try { if (token) await api('mobile/logout', 'POST', {}); } catch { /* Expired tokens can still be removed locally. */ }
    await SecureStore.deleteItemAsync(TOKEN_KEY).catch(() => {});
    setToken(null); setProfile(null); setApplications([]); setCourses([]); setMatches([]); setCourse(null);
    setPassword(''); setOtp(''); setDeletePassword(''); setDeleteOtp(''); setProfileName(''); setSubjectScores(['', '', '', '', '', '', '']);
    setMessage('You are signed out.');
  }

  async function openCourse(item: Course) {
    setCourse(item); setSelected([]); setMatches([]); setMessage('');
    try {
      const data = await api(`courses/${item.id}/matches`);
      setMatches(data.matches || []);
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Could not load course matches.'); }
  }

  async function applySelected() {
    if (!course || selected.length === 0) return;
    setBusy(true);
    try {
      await api('applications/create', 'POST', { course_id: course.id, university_ids: selected, consent_to_share: true });
      setMessage('Your demo applications were submitted to the selected universities.');
      setSelected([]); await loadData(); setTab('applications');
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Could not submit applications.'); }
    finally { setBusy(false); }
  }

  async function decide(application: Application, decision: 'accepted' | 'rejected') {
    try { await api(`applications/${application.id}/decision`, 'POST', { decision }); await loadData(); setMessage(`Offer ${decision}.`); }
    catch (error) { setMessage(error instanceof Error ? error.message : 'Could not update offer.'); }
  }

  async function saveProfile() {
    const scoreAt = (index: number) => index === 0 ? Number(english) : index === 1 ? Number(math) : Number(subjectScores[index]);
    const subjects: Record<string, number> = {};
    subjectNames.forEach((name, index) => { if (name.trim()) subjects[name.trim()] = scoreAt(index); });
    const distinctNames = Object.keys(subjects).map((name) => name.toLowerCase());
    const allMarks = [aps, ...subjectNames.map((_, index) => scoreAt(index))];
    const missingSubjectMark = subjectNames.some((_, index) => (index === 0 ? english : index === 1 ? math : subjectScores[index]) === '');
    if (!profileName.trim() || Object.keys(subjects).length !== 7 || !('Life Orientation' in subjects) || new Set(distinctNames).size !== 7 || !aps || missingSubjectMark || allMarks.some((mark) => !Number.isInteger(mark) || mark < 0 || mark > 100) || Number(aps) > 50) {
      setMessage('Enter your name, APS, required marks, and seven unique subjects including Life Orientation, with a mark for each.');
      return;
    }
    const next = { name: profileName.trim(), email: profile?.email || accountEmail, marks: { aps: Number(aps), mathematics: Number(math), english: Number(english), subjects }, upgrading };
    setBusy(true);
    try { const result = await api('profile/update', 'POST', { profile: next }); setProfile(result.profile); setMessage('Profile saved securely.'); }
    catch (error) { setMessage(error instanceof Error ? error.message : 'Could not save your profile.'); }
    finally { setBusy(false); }
  }

  async function submitResidence(applicationId: string) {
    try {
      await api(`applications/${applicationId}/residence`, 'POST', { preference: residencePreference, accommodation_needs: accommodationNeeds });
      setResidenceTarget(''); setAccommodationNeeds(''); await loadData(); setMessage('Your demo residence preference is recorded.');
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Could not record residence preference.'); }
  }

  async function showFunding() {
    try {
      const data = await api('funding-plan');
      setFundingMessage(data.status === 'no_accepted_offer' ? 'Accept a study offer to see its funding destination summary.' : `${data.course_name} · ${data.university_name} · ${data.sent_to_nsfas ? 'Sent to NSFAS' : 'Demo summary only; not sent to NSFAS'}`);
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Could not load the funding summary.'); }
  }

  async function exportPersonalData() {
    try {
      const data = await api('privacy/export');
      await Share.share({ title: 'UniPath personal information', message: JSON.stringify(data, null, 2) });
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Could not export your information.'); }
  }

  async function deleteAccount() {
    if (!deletePassword || deleteOtp.length !== 6) { setMessage('Enter your password and current six-digit authenticator code to delete the account.'); return; }
    Alert.alert('Delete UniPath account?', 'This permanently deletes your account and associated demo records.', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Delete account', style: 'destructive', onPress: async () => {
        try {
          await api('privacy/delete-account', 'POST', { password: deletePassword, otp_token: deleteOtp });
          await SecureStore.deleteItemAsync(TOKEN_KEY); setToken(null); setMessage('Your account and demo records were deleted.');
        } catch (error) { setMessage(error instanceof Error ? error.message : 'Could not delete the account.'); }
      } },
    ]);
  }

  const theme = highContrast ? contrast : palette;
  const scaled = (size: number) => ({ fontSize: size });

  if (!token) return <TextScale.Provider value={readScale}><SafeAreaView style={[styles.safe, { backgroundColor: theme.bg }]}>
    <StatusBar style={highContrast ? 'light' : 'dark'} />
    <ScrollView contentContainerStyle={styles.loginContainer} keyboardShouldPersistTaps="handled">
      <Text style={[styles.brand, { color: theme.teal }, scaled(34)]}>UniPath</Text>
      <Text accessibilityRole="header" style={[styles.heading, { color: theme.ink }, scaled(27)]}>Your university journey, together.</Text>
      <Text style={[styles.body, { color: theme.muted }, scaled(17)]}>Sign in with your account password and current authenticator code.</Text>
      <View style={styles.tools}><Button title="A−" secondary onPress={() => setReadScale(Math.max(.9, readScale - .1))} /><Text style={[styles.hint, { color: theme.muted }]}>Text size</Text><Button title="A+" secondary onPress={() => setReadScale(Math.min(1.4, readScale + .1))} /><Button title="Read aloud" secondary onPress={() => speak('UniPath sign in. Enter your email, password, and current authenticator code.')} /></View>
      <Field label="Email address" value={email} onChangeText={setEmail} keyboardType="email-address" />
      <Field label="Password" value={password} onChangeText={setPassword} secureTextEntry />
      <Field label="Authenticator code" value={otp} onChangeText={setOtp} keyboardType="numeric" hint="Enter the current six-digit code from your authenticator app." />
      {message ? <Text accessibilityRole="alert" style={[styles.notice, { color: theme.ink }]}>{message}</Text> : null}
      <Button title={busy ? 'Signing in…' : 'Sign in securely'} onPress={signIn} disabled={busy || !email || !password || otp.length !== 6} />
      {busy ? <ActivityIndicator accessibilityLabel="Loading" color={theme.teal} /> : null}
      <Button title="Create account and set up 2FA" secondary onPress={() => Linking.openURL(`${API}/auth/register/`)} />
      <Text style={[styles.hint, { color: theme.muted }]}>Create your account and set up 2FA in the UniPath web app before signing in here.</Text>
      <Button title={highContrast ? 'Standard colors' : 'High contrast'} secondary onPress={() => setHighContrast(!highContrast)} />
    </ScrollView>
  </SafeAreaView></TextScale.Provider>;

  const filteredCourses = courses.filter((item) => `${item.name || item.short_name || ''} ${item.faculty}`.toLowerCase().includes(search.toLowerCase()));
  return <TextScale.Provider value={readScale}><SafeAreaView style={[styles.safe, { backgroundColor: theme.bg }]}>
    <StatusBar style={highContrast ? 'light' : 'dark'} />
    <View style={[styles.header, { backgroundColor: theme.surface, borderColor: theme.line }]}>
      <View><Text style={[styles.brandSmall, { color: theme.teal }, scaled(23)]}>UniPath</Text><Text style={[styles.hint, { color: theme.muted }]}>One journey. Many universities.</Text></View>
      <View style={styles.headerActions}><Button title="A−" secondary onPress={() => setReadScale(Math.max(.9, readScale - .1))} /><Button title="A+" secondary onPress={() => setReadScale(Math.min(1.4, readScale + .1))} /><Button title={highContrast ? 'Contrast on' : 'Contrast'} secondary onPress={() => setHighContrast(!highContrast)} /><Button title="Read aloud" secondary onPress={() => speak(tab === 'courses' ? 'Explore courses. Browse programmes and compare universities.' : tab === 'applications' ? 'My applications. Review study offers and residence requests.' : 'My profile. Update your marks and privacy settings.')} /></View>
    </View>
    {message ? <Text accessibilityRole="status" style={[styles.notice, { color: theme.ink }]}>{message}</Text> : null}
    <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
      {busy ? <ActivityIndicator accessibilityLabel="Loading" color={theme.teal} /> : null}
      {tab === 'courses' ? <>
        <Text accessibilityRole="header" style={[styles.heading, { color: theme.ink }, scaled(26)]}>{course ? course.name || course.short_name : 'Explore courses'}</Text>
        {course ? <>
          <Text style={[styles.tag, { color: theme.teal }]}>{course.faculty}</Text>
          <Text style={[styles.body, { color: theme.muted }, scaled(16)]}>{course.description || 'Explore this programme and the universities offering it.'}</Text>
          {course.careers?.length ? <Text style={[styles.body, { color: theme.ink }, scaled(15)]}>Career examples: {course.careers.join(', ')}</Text> : null}
          <Text style={[styles.sectionTitle, { color: theme.ink }, scaled(19)]}>University matches</Text>
          {!profile ? <Text style={[styles.hint, { color: theme.muted }]}>Add your seven-subject profile, including Life Orientation, to see matches.</Text> : null}
          {matches.map((match) => {
            const disabled = match.status === 'does_not_match';
            const checked = selected.includes(match.university.id);
            return <Pressable key={match.university.id} accessibilityRole="checkbox" accessibilityState={{ checked, disabled }} accessibilityLabel={`${match.university.name}. ${match.status.replaceAll('_', ' ')}`} onPress={() => !disabled && setSelected(checked ? selected.filter((id) => id !== match.university.id) : [...selected, match.university.id])} style={[styles.card, { backgroundColor: theme.surface, borderColor: theme.line }, disabled && styles.disabled]}>
              <Text style={[styles.cardTitle, { color: theme.ink }, scaled(18)]}>{checked ? '☑ ' : '☐ '}{match.university.name}</Text>
              <Text style={[styles.body, { color: theme.muted }]}>Illustrative requirements: APS {match.requirements.aps} · Mathematics {match.requirements.mathematics}% · Language {match.requirements.english}%</Text>
              <Text style={[styles.tag, { color: disabled ? theme.red : theme.teal }]}>{match.status.replaceAll('_', ' ')}</Text>
            </Pressable>;
          })}
          <Button title="Apply to selected universities" onPress={applySelected} disabled={busy || selected.length === 0 || !profile} />
          <Button title="Back to courses" secondary onPress={() => setCourse(null)} />
        </> : <>
          <Text style={[styles.body, { color: theme.muted }, scaled(16)]}>Browse programmes by faculty, see career examples, and compare illustrative entry requirements.</Text>
          <Field label="Search by course or faculty" value={search} onChangeText={setSearch} />
          {filteredCourses.map((item) => <View key={item.id} style={[styles.card, { backgroundColor: theme.surface, borderColor: theme.line }]}>
            <Text style={[styles.tag, { color: theme.teal }]}>{item.faculty}</Text>
            <Text style={[styles.cardTitle, { color: theme.ink }, scaled(19)]}>{item.name || item.short_name}</Text>
            <Text style={[styles.body, { color: theme.muted }]}>{item.description || ''}</Text>
            {item.careers?.length ? <Text style={[styles.hint, { color: theme.muted }]}>Careers: {item.careers.slice(0, 3).join(', ')}</Text> : null}
            <Button title="View course and university matches" onPress={() => openCourse(item)} />
          </View>)}
          {filteredCourses.length === 0 ? <Text style={[styles.body, { color: theme.muted }]}>No courses match that search.</Text> : null}
        </>}
      </> : null}

      {tab === 'profile' ? <>
        <Text accessibilityRole="header" style={[styles.heading, { color: theme.ink }, scaled(26)]}>My student profile</Text>
        <Text style={[styles.body, { color: theme.muted }]}>Your information is encrypted in the demo database. Enter seven unique matric subjects, including Life Orientation.</Text>
        <Field label="Full name" value={profileName} onChangeText={setProfileName} />
        <Field label="Account email" value={profile?.email || accountEmail} onChangeText={() => {}} hint="Account email is managed by your sign-in account." />
        <Field label="APS (enter according to institution rules)" value={aps} onChangeText={setAps} keyboardType="numeric" />
        <Text style={[styles.sectionTitle, { color: theme.ink }]}>Seven matric subjects</Text>
        {subjectNames.map((name, index) => <View key={index} style={[styles.subjectRow, { backgroundColor: theme.surface, borderColor: theme.line }]}>
          <TextInput accessibilityLabel={`Subject ${index + 1} name${index === 2 ? ', Life Orientation required' : ''}`} accessibilityHint={index === 2 ? 'This must be Life Orientation.' : 'Enter a unique matric subject name.'} style={[styles.subjectInput, { color: theme.ink, borderColor: theme.line }]} value={name} editable={index !== 2} onChangeText={(value) => setSubjectNames(subjectNames.map((item, n) => n === index ? value : item))} placeholder={index === 2 ? 'Life Orientation' : `Subject ${index + 1}`} />
          <TextInput accessibilityLabel={`${name || `Subject ${index + 1}`} mark percentage`} style={[styles.scoreInput, { color: theme.ink, borderColor: theme.line }]} value={index === 0 ? english : index === 1 ? math : subjectScores[index]} onChangeText={(value) => index === 0 ? setEnglish(value) : index === 1 ? setMath(value) : setSubjectScores(subjectScores.map((item, n) => n === index ? value : item))} keyboardType="numeric" placeholder="%" />
        </View>)}
        <View style={styles.switchRow}><Text style={[styles.label, { color: theme.ink }]}>I am upgrading my marks</Text><Switch accessibilityLabel="I am upgrading my marks" value={upgrading} onValueChange={setUpgrading} trackColor={{ true: theme.teal }} /></View>
        <Button title="Save profile securely" onPress={saveProfile} disabled={busy} />
        <Button title="Read profile instructions aloud" secondary onPress={() => speak('Your profile needs a name, an APS score, mathematics and language marks, and seven unique subjects. Life Orientation is required.')} />
        <Text style={[styles.sectionTitle, { color: theme.ink }]}>Privacy and account controls</Text>
        <Text style={[styles.hint, { color: theme.muted }]}>Export a copy of your data, or delete the demo account after confirming your password and authenticator code.</Text>
        <Button title="Export my personal information" secondary onPress={exportPersonalData} />
        <Field label="Password to confirm account deletion" value={deletePassword} onChangeText={setDeletePassword} secureTextEntry />
        <Field label="Current authenticator code" value={deleteOtp} onChangeText={setDeleteOtp} keyboardType="numeric" />
        <Button title="Delete account and demo records" secondary onPress={deleteAccount} />
      </> : null}

      {tab === 'applications' ? <>
        <Text accessibilityRole="header" style={[styles.heading, { color: theme.ink }, scaled(26)]}>My applications</Text>
        <Text style={[styles.body, { color: theme.muted }]}>Offers are simulated in this prototype. No university or NSFAS is contacted.</Text>
        {applications.map((application) => {
          const residence = residences.find((item) => item.application_id === application.id);
          return <View key={application.id} style={[styles.card, { backgroundColor: theme.surface, borderColor: theme.line }]}>
            <Text style={[styles.cardTitle, { color: theme.ink }, scaled(18)]}>{application.course_name}</Text>
            <Text style={[styles.body, { color: theme.muted }]}>{application.university_name}</Text>
            <Text style={[styles.tag, { color: theme.teal }]}>Status: {application.status.replaceAll('_', ' ')}</Text>
            {application.status === 'offer_received' ? <View style={styles.buttonRow}><Button title="Accept offer" onPress={() => decide(application, 'accepted')} /><Button title="Reject offer" secondary onPress={() => decide(application, 'rejected')} /></View> : null}
            {application.status === 'accepted' && !residence ? <>
              {residenceTarget === application.id ? <>
                <Text style={[styles.label, { color: theme.ink }]}>Choose residence preference</Text>
                {['On-campus residence', 'Off-campus accommodation support', 'Either option'].map((option) => <Pressable key={option} accessibilityRole="radio" accessibilityState={{ checked: residencePreference === option }} onPress={() => setResidencePreference(option)} style={styles.radioRow}><Text style={[styles.body, { color: theme.ink }]}>{residencePreference === option ? '◉' : '○'} {option}</Text></Pressable>)}
                <Field label="Optional accommodation or accessibility needs" value={accommodationNeeds} onChangeText={setAccommodationNeeds} hint="Maximum 500 characters. Use fictional information in this demo." />
                <Button title="Record demo residence request" onPress={() => submitResidence(application.id)} />
              </> : <Button title="Apply for residence" onPress={() => { setResidenceTarget(application.id); setResidencePreference('On-campus residence'); }} />}
            </> : null}
            {residence ? <Text style={[styles.body, { color: theme.muted }]}>Residence: {residence.preference} ({residence.status.replaceAll('_', ' ')})</Text> : null}
          </View>;
        })}
        {!applications.length ? <Text style={[styles.body, { color: theme.muted }]}>No applications yet. Explore courses and apply to universities that offer your chosen course.</Text> : null}
        <Button title="Show funding destination summary" onPress={showFunding} />
        {fundingMessage ? <Text accessibilityRole="summary" style={[styles.card, { color: theme.ink, backgroundColor: theme.surface, borderColor: theme.line }]}>{fundingMessage}</Text> : null}
      </> : null}
    </ScrollView>
    <View style={[styles.tabBar, { backgroundColor: theme.surface, borderColor: theme.line }]}>
      {(['courses', 'applications', 'profile'] as const).map((name) => <Pressable key={name} accessibilityRole="tab" accessibilityState={{ selected: tab === name }} onPress={() => { setTab(name); setCourse(null); }} style={styles.tab}>
        <Text style={[styles.tabText, { color: tab === name ? theme.teal : theme.muted }, scaled(13)]}>{name === 'courses' ? 'Explore' : name === 'applications' ? 'Applications' : 'Profile'}</Text>
      </Pressable>)}
      <Pressable accessibilityRole="button" accessibilityLabel="Sign out" onPress={signOut} style={styles.tab}><Text style={[styles.tabText, { color: theme.red }]}>Sign out</Text></Pressable>
    </View>
  </SafeAreaView></TextScale.Provider>;
}

const palette = { bg: '#f4f7f6', surface: '#ffffff', ink: '#142c28', muted: '#4a625d', teal: '#0c574d', line: '#cbd8d4', red: '#982b24' };
const contrast = { bg: '#000000', surface: '#080808', ink: '#ffffff', muted: '#f0f0f0', teal: '#ffeb3b', line: '#ffffff', red: '#ff9d91' };
const styles = StyleSheet.create({
  safe: { flex: 1 }, loginContainer: { flexGrow: 1, padding: 22, gap: 16, justifyContent: 'center' },
  header: { paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 1, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 8 },
  headerActions: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'flex-end', gap: 5 }, brand: { fontWeight: '900', letterSpacing: -1 }, brandSmall: { fontWeight: '900', letterSpacing: -0.6 },
  heading: { fontWeight: '800', letterSpacing: -0.4, marginTop: 8 }, sectionTitle: { fontSize: 19, fontWeight: '800', marginTop: 8 }, body: { fontSize: 15, lineHeight: 23 }, hint: { fontSize: 13, lineHeight: 19 }, notice: { paddingHorizontal: 16, paddingVertical: 9, fontSize: 14, fontWeight: '600' },
  content: { padding: 16, gap: 12, paddingBottom: 28 }, fieldWrap: { gap: 6, marginVertical: 2 }, label: { fontSize: 15, lineHeight: 21, fontWeight: '700' }, input: { minHeight: 50, borderWidth: 1, borderColor: '#82909b', borderRadius: 10, paddingHorizontal: 12, paddingVertical: 10, color: '#142c28', backgroundColor: '#ffffff', fontSize: 16 },
  button: { minHeight: 48, borderRadius: 10, paddingVertical: 12, paddingHorizontal: 16, backgroundColor: '#0c574d', alignItems: 'center', justifyContent: 'center', marginVertical: 3 }, buttonText: { color: '#ffffff', fontSize: 15, fontWeight: '800', textAlign: 'center' }, buttonSecondary: { backgroundColor: '#ffffff', borderWidth: 1, borderColor: '#82909b' }, buttonSecondaryText: { color: '#142c28' }, disabled: { opacity: 0.45 }, pressed: { opacity: 0.75 },
  card: { borderWidth: 1, borderRadius: 14, padding: 15, gap: 9, marginVertical: 3 }, cardTitle: { fontSize: 17, fontWeight: '800', lineHeight: 24 }, tag: { fontSize: 13, lineHeight: 19, fontWeight: '800', textTransform: 'capitalize' }, tools: { flexDirection: 'row', alignItems: 'center', flexWrap: 'wrap', gap: 7 },
  subjectRow: { minHeight: 58, flexDirection: 'row', alignItems: 'center', gap: 8, borderWidth: 1, borderRadius: 10, padding: 7 }, subjectInput: { flex: 1, minHeight: 43, borderWidth: 1, borderRadius: 8, paddingHorizontal: 8, fontSize: 14, backgroundColor: 'transparent' }, scoreInput: { width: 72, minHeight: 43, borderWidth: 1, borderRadius: 8, textAlign: 'center', fontSize: 15, backgroundColor: 'transparent' }, switchRow: { minHeight: 54, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  buttonRow: { flexDirection: 'row', gap: 8 }, radioRow: { minHeight: 44, justifyContent: 'center' }, tabBar: { flexDirection: 'row', minHeight: 62, borderTopWidth: 1, paddingVertical: 7, paddingHorizontal: 5, justifyContent: 'space-around', alignItems: 'center' }, tab: { minHeight: 46, paddingHorizontal: 7, justifyContent: 'center', alignItems: 'center' }, tabText: { fontSize: 13, fontWeight: '800' },
});
