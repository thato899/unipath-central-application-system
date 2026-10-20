const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

const state = {
  courses: [],
  profile: null,
  selectedCourse: null,
  matches: [],
  selectedUniversities: new Set(),
  applications: [],
  residenceApplications: [],
  activeResidenceApplicationId: null,
  selectedFaculty: "All faculties",
};

function announce(message) { $("#live-status").textContent = message; }

function csrfToken() { return $("meta[name='csrf-token']")?.content || $("input[name='csrfmiddlewaretoken']")?.value || ""; }

async function postJson(url, payload) {
  return fetch(url, {
    method: "POST", headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
    body: JSON.stringify(payload), credentials: "same-origin",
  });
}

function navigate(pageName) {
  $$(".page").forEach((page) => page.classList.add("hidden"));
  const page = $("#page-" + pageName);
  if (page) page.classList.remove("hidden");
  $$(".nav-link").forEach((button) => {
    const active = button.dataset.page === pageName;
    button.classList.toggle("active", active);
    if (active) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
  if (page) {
    page.setAttribute("tabindex", "-1");
    page.focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: "instant" });
  }
}

function profileFromForm() {
  const subjects = {
    "Home or First Additional Language": Number($("#english").value), Mathematics: Number($("#mathematics").value),
    "Life Orientation": Number($("#life-orientation").value),
  };
  [4, 5, 6, 7].forEach((n) => { subjects[$("#subject-" + n + "-name").value.trim()] = Number($("#subject-" + n).value); });
  return {
    name: $("#student-name").value.trim(),
    email: $("#student-email").value.trim(),
    marks: { aps: Number($("#aps").value), mathematics: subjects.Mathematics, english: subjects["Home or First Additional Language"], subjects },
    upgrading: $("#upgrading").checked,
  };
}

function restoreProfileForm() {
  if (!state.profile) return;
  $("#student-name").value = state.profile.name || "";
  $("#student-email").value = state.profile.email || "";
  $("#aps").value = state.profile.marks?.aps ?? "";
  $("#mathematics").value = state.profile.marks?.mathematics ?? "";
  $("#english").value = state.profile.marks?.english ?? "";
  const subjects = state.profile.marks?.subjects || {};
  $("#life-orientation").value = subjects["Life Orientation"] ?? "";
  [4, 5, 6, 7].forEach((n) => { $("#subject-" + n).value = subjects["Subject " + n] ?? ""; });
  [4, 5, 6, 7].forEach((n) => {
    const savedName = Object.keys(subjects).filter((name) => !["Home or First Additional Language", "Mathematics", "Life Orientation"].includes(name))[n - 3];
    $("#subject-" + n + "-name").value = savedName || $("#subject-" + n + "-name").value;
    if (savedName) $("#subject-" + n).value = subjects[savedName];
  });
  $("#upgrading").checked = Boolean(state.profile.upgrading);
}

function currentMarksQuery() {
  const marks = state.profile?.marks || {};
  return new URLSearchParams({
    aps: String(marks.aps || 0), mathematics: String(marks.mathematics || 0),
    english: String(marks.english || 0), upgrading: String(Boolean(state.profile?.upgrading)),
  }).toString();
}

function badge(text, kind = "teal") {
  const span = document.createElement("span");
  span.className = "status-badge " + kind;
  span.textContent = text;
  return span;
}

function makeButton(text, className, onClick) {
  const button = document.createElement("button");
  button.className = "button " + className;
  button.type = "button";
  button.textContent = text;
  button.addEventListener("click", onClick);
  return button;
}

function renderFaculties() {
  const faculties = ["All faculties", ...new Set(state.courses.map((course) => course.faculty))];
  const list = $("#faculty-list");
  list.replaceChildren();
  faculties.forEach((faculty) => {
    const button = document.createElement("button");
    button.className = "faculty-button";
    button.type = "button";
    button.textContent = faculty;
    button.setAttribute("aria-pressed", String(state.selectedFaculty === faculty));
    button.addEventListener("click", () => {
      state.selectedFaculty = faculty;
      renderFaculties();
      renderCourses();
    });
    list.append(button);
  });
}

function renderCourses() {
  const list = $("#course-list");
  list.replaceChildren();
  const visible = state.courses.filter((course) => state.selectedFaculty === "All faculties" || course.faculty === state.selectedFaculty);
  visible.forEach((course) => {
    const article = document.createElement("article");
    article.className = "course-card";
    const faculty = document.createElement("span");
    faculty.className = "faculty-tag";
    faculty.textContent = course.faculty;
    const title = document.createElement("h2");
    title.textContent = course.name;
    const description = document.createElement("p");
    description.textContent = course.description;
    const careerLabel = document.createElement("strong");
    careerLabel.textContent = "Example careers";
    const careers = document.createElement("ul");
    careers.className = "career-list";
    course.careers.forEach((career) => {
      const item = document.createElement("li");
      item.textContent = career;
      careers.append(item);
    });
    const footer = document.createElement("div");
    footer.className = "course-card-footer";
    const count = document.createElement("span");
    count.className = "help";
    count.textContent = course.match_count + " sample " + (course.match_count === 1 ? "university" : "universities") + " listed";
    footer.append(count, makeButton("View course and universities", "primary", () => openMatches(course.id)));
    article.append(faculty, title, description, careerLabel, careers, footer);
    list.append(article);
  });
}

async function openMatches(courseId) {
  state.selectedCourse = state.courses.find((course) => course.id === courseId);
  if (!state.selectedCourse || !state.profile) return;
  const response = await fetch("/api/courses/" + courseId + "/matches", { credentials: "same-origin" });
  const data = await response.json();
  state.matches = data.matches || [];
  state.selectedUniversities = new Set(state.matches
    .filter((match) => match.status === "meets_requirements")
    .map((match) => match.university.id));
  renderMatches();
  navigate("matches");
}

function renderMatches() {
  const course = state.selectedCourse;
  $("#matches-breadcrumb").textContent = "Explore courses / " + course.faculty;
  $("#matches-title").textContent = course.short_name;
  $("#matches-description").textContent = course.description;
  $("#matches-careers").textContent = "Example careers: " + course.careers.join(" · ");
  const eligible = state.matches.filter((match) => match.status === "meets_requirements").length;
  $("#match-summary").replaceChildren(badge(
    eligible ? eligible + " university " + (eligible === 1 ? "meets" : "universities meet") + " listed requirements" : "No current requirements match",
    eligible ? "green" : "amber",
  ));
  const list = $("#match-list");
  list.replaceChildren();
  state.matches.forEach((match) => {
    const article = document.createElement("article");
    article.className = "match-card";
    const text = match.status === "meets_requirements" ? "Meets listed requirements"
      : match.status === "apply_while_upgrading" ? "Apply while upgrading" : "Does not match current marks";
    const kind = match.status === "meets_requirements" ? "green" : match.status === "apply_while_upgrading" ? "amber" : "red";
    article.append(badge(text, kind));
    const title = document.createElement("h3");
    title.textContent = match.university.name;
    const sample = document.createElement("p");
    sample.className = "help";
    sample.textContent = (match.university.sample ? "Demo institution" : "Programme catalogue example") + " · " + match.university.region;
    const requirements = document.createElement("div");
    requirements.className = "requirements";
    const reqTitle = document.createElement("strong");
    reqTitle.textContent = "Illustrative demo thresholds — confirm with the university";
    const reqText = document.createElement("p");
    reqText.textContent = "APS " + match.requirements.aps + "+ · Mathematics " + match.requirements.mathematics + "% · English " + match.requirements.english + "%";
    requirements.append(reqTitle, reqText);
    const marks = document.createElement("p");
    marks.textContent = "Your marks: APS " + state.profile.marks.aps + " · Mathematics " + state.profile.marks.mathematics + "% · Language " + state.profile.marks.english + "% · Life Orientation included in your seven-subject record";
    article.append(title, sample, requirements, marks);
    if (match.status !== "does_not_match") {
      const label = document.createElement("label");
      label.className = "select-row";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = state.selectedUniversities.has(match.university.id);
      checkbox.setAttribute("aria-label", "Apply to " + match.university.name);
      checkbox.addEventListener("change", () => {
        if (checkbox.checked) state.selectedUniversities.add(match.university.id);
        else state.selectedUniversities.delete(match.university.id);
        updateSelectedCount();
      });
      const labelText = document.createElement("span");
      labelText.textContent = match.status === "apply_while_upgrading" ? "Include application while upgrading" : "Apply to this university";
      label.append(checkbox, labelText);
      article.append(label);
    } else {
      const note = document.createElement("p");
      note.className = "help";
      note.textContent = "This sample course does not show an upgrading pathway for your current marks.";
      article.append(note);
    }
    list.append(article);
  });
  updateSelectedCount();
}

function updateSelectedCount() {
  const count = state.selectedUniversities.size;
  $("#selected-count").textContent = count ? count + " " + (count === 1 ? "university" : "universities") + " selected" : "No universities selected";
  $("#review-applications").disabled = count === 0;
}

function renderReview() {
  $("#application-consent").checked = false;
  $("#review-profile").textContent = state.profile.name + " · " + state.profile.email;
  $("#review-marks").textContent = "APS " + state.profile.marks.aps + " · 7 matric subjects recorded, including Life Orientation";
  const chosen = state.matches.filter((match) => state.selectedUniversities.has(match.university.id));
  $("#review-count").textContent = chosen.length + " " + (chosen.length === 1 ? "application" : "applications") + " selected";
  const list = $("#review-list");
  list.replaceChildren();
  chosen.forEach((match) => {
    const article = document.createElement("article");
    article.className = "review-card";
    const info = document.createElement("div");
    const title = document.createElement("h3");
    title.textContent = state.selectedCourse.short_name + " · " + match.university.name;
    const details = document.createElement("p");
    details.textContent = match.status === "apply_while_upgrading" ? "You indicated that you are upgrading marks." : "Your marks meet the listed sample requirements.";
    info.append(title, details);
    article.append(badge(match.status === "apply_while_upgrading" ? "Upgrading pathway" : "Meets listed requirements", match.status === "apply_while_upgrading" ? "amber" : "green"), info);
    list.append(article);
  });
}

function statusPresentation(application) {
  const known = {
    offer_received: ["Offer received", "green"], in_review: ["Application submitted · Awaiting university decision", "teal"],
    accepted: ["Offer accepted", "green"], rejected: ["Offer declined", "red"],
  };
  return known[application.status] || ["Status update", "teal"];
}

function renderApplications() {
  const list = $("#application-list");
  list.replaceChildren();
  $("#empty-applications").classList.toggle("hidden", state.applications.length > 0);
  $("#application-summary").classList.toggle("hidden", state.applications.length === 0);
  if (!state.applications.length) return;
  const offers = state.applications.filter((app) => app.status === "offer_received").length;
  const acceptedOfferExists = state.applications.some((app) => app.status === "accepted");
  const heading = document.createElement("h2");
  heading.textContent = state.applications.length + " " + (state.applications.length === 1 ? "application" : "applications");
  const description = document.createElement("p");
  description.textContent = offers + " sample " + (offers === 1 ? "offer received" : "offers received");
  $("#application-summary").replaceChildren(heading, description);
  state.applications.forEach((application) => {
    const article = document.createElement("article");
    article.className = "application-card";
    const info = document.createElement("div");
    info.className = "application-main";
    const title = document.createElement("h3");
    title.textContent = application.university_name + " · " + application.course_name;
    const detail = document.createElement("p");
    const presentation = statusPresentation(application);
    detail.textContent = presentation[0];
    const status = badge(presentation[0], presentation[1]);
    const note = document.createElement("p");
    note.className = "help";
    note.textContent = application.demo_response ? "Sample response for this demo" : "Sample application";
    info.append(title, detail, note);
    article.append(status, info);
    const residence = state.residenceApplications.find((item) => item.application_id === application.id);
    if (application.status === "accepted") {
      const actions = document.createElement("div");
      actions.className = "offer-actions";
      if (residence) {
        const residenceStatus = document.createElement("p");
        residenceStatus.className = "help";
        residenceStatus.textContent = "Residence request recorded: " + residence.preference;
        article.append(residenceStatus);
        actions.append(makeButton("View funding destination", "secondary", loadFundingPlan));
      } else {
        actions.append(makeButton("Apply for residence", "primary", () => openResidence(application.id)));
      }
      article.append(actions);
    }
    if (application.status === "offer_received") {
      const actions = document.createElement("div");
      actions.className = "offer-actions";
      const acceptButton = makeButton("Accept offer", "primary", () => decideOffer(application.id, "accepted"));
      acceptButton.disabled = acceptedOfferExists;
      if (acceptedOfferExists) acceptButton.title = "Only one offer can be accepted in this single-student demo.";
      actions.append(
        acceptButton,
        makeButton("Reject offer", "danger", () => decideOffer(application.id, "rejected")),
      );
      article.append(actions);
    }
    list.append(article);
  });
}

async function decideOffer(applicationId, decision) {
  const response = await postJson("/api/applications/" + applicationId + "/decision", { decision });
  const data = await response.json();
  if (!response.ok) return announce(data.error || "The offer could not be updated.");
  state.applications = state.applications.map((app) => app.id === applicationId ? data.application : app);
  renderApplications();
  const accepted = decision === "accepted";
  $("#offer-icon").textContent = "✓";
  $("#offer-icon").style.background = accepted ? "var(--green-soft)" : "var(--red-soft)";
  $("#offer-icon").style.color = accepted ? "var(--green)" : "var(--red)";
  $("#offer-title").textContent = accepted ? "Offer accepted" : "Offer declined";
  $("#offer-message").textContent = "You " + (accepted ? "accepted" : "declined") + " the offer for " + data.application.course_name + " at " + data.application.university_name + ".";
  $("#offer-details").textContent = accepted
    ? "Your response is recorded in this local demo. No real institution has been contacted."
    : "Your response is recorded in this local demo. Your other applications remain in the tracker.";
  $("#residence-next-step").classList.toggle("hidden", !accepted);
  if (accepted) {
    $("#start-residence").onclick = () => openResidence(applicationId);
    $("#view-funding-plan").onclick = loadFundingPlan;
  }
  navigate("offer");
  announce(accepted ? "Offer accepted in the demo." : "Offer declined in the demo.");
}

async function openResidence(applicationId) {
  const application = state.applications.find((item) => item.id === applicationId);
  if (!application || application.status !== "accepted") return announce("Accept an offer before applying for residence.");
  if (state.residenceApplications.some((item) => item.application_id === applicationId)) return loadFundingPlan();
  state.activeResidenceApplicationId = applicationId;
  $("#residence-university").textContent = "Requesting accommodation related to " + application.course_name + " at " + application.university_name + ".";
  $("#residence-preference").value = "";
  $("#accommodation-needs").value = "";
  navigate("residence");
}

async function submitResidenceApplication(event) {
  event.preventDefault();
  if (!state.activeResidenceApplicationId || !event.currentTarget.reportValidity()) return;
  const response = await postJson("/api/applications/" + state.activeResidenceApplicationId + "/residence", {
    preference: $("#residence-preference").value, accommodation_needs: $("#accommodation-needs").value.trim(),
  });
  const data = await response.json();
  if (!response.ok) return announce(data.error || "The residence request could not be recorded.");
  state.residenceApplications.push(data.residence_application);
  renderApplications();
  announce("Residence preference recorded for " + data.residence_application.university_name + ". No university has been contacted.");
  await loadFundingPlan();
}

async function loadFundingPlan() {
  const response = await fetch("/api/funding-plan");
  const data = await response.json();
  const panel = $("#funding-plan");
  panel.replaceChildren();
  const heading = document.createElement("h2");
  const details = document.createElement("p");
  const status = document.createElement("p");
  if (data.status === "no_accepted_offer") {
    heading.textContent = "No accepted offer yet";
    details.textContent = "Accept one university offer to identify a funding destination.";
    status.textContent = "No destination has been selected.";
  } else {
    heading.textContent = data.university_name;
    details.textContent = "Accepted programme: " + data.course_name + ".";
    status.textContent = data.residence_status === "not_submitted"
      ? "Residence preference: not recorded yet. Submit a residence request to complete this demo summary."
      : "Residence preference: " + data.residence_preference + " (request recorded in this demo).";
  }
  const notice = document.createElement("p");
  notice.className = "help";
  notice.textContent = data.sent_to_nsfas ? "Sent to NSFAS." : "Demo only: this destination summary is not sent to NSFAS.";
  panel.append(heading, details, status, notice);
  const residenceButton = $("#funding-apply-residence");
  residenceButton.classList.toggle("hidden", data.status !== "waiting_for_residence");
  if (data.status === "waiting_for_residence") {
    residenceButton.onclick = () => openResidence(data.application_id);
  }
  navigate("funding");
}

async function submitApplications() {
  if (!$("#application-consent").checked) return announce("Confirm consent to share your profile with the selected institutions before submitting.");
  const response = await postJson("/api/applications/create", {
    course_id: state.selectedCourse.id, university_ids: [...state.selectedUniversities], consent_to_share: true,
  });
  const data = await response.json();
  if (!response.ok) return announce(data.error || "Applications could not be submitted.");
  state.applications = [...state.applications, ...data.applications];
  renderApplications();
  navigate("applications");
  announce(data.applications.length + " demo applications submitted.");
}

async function loadApplications() {
  const [applicationsResponse, residenceResponse] = await Promise.all([fetch("/api/applications"), fetch("/api/residence")]);
  const [data, residenceData] = await Promise.all([applicationsResponse.json(), residenceResponse.json()]);
  state.applications = data.applications || [];
  state.residenceApplications = residenceData.residence_applications || [];
  renderApplications();
}

async function start() {
  const [response, profileResponse] = await Promise.all([fetch("/api/courses"), fetch("/api/profile")]);
  const [data, profileData] = await Promise.all([response.json(), profileResponse.json()]);
  state.courses = data.courses || [];
  state.profile = profileData.profile || null;
  if (!state.profile) $("#student-email").value = profileData.account_email || "";
  renderFaculties();
  renderCourses();
  restoreProfileForm();
  await loadApplications();
  const savedSubjects = state.profile?.marks?.subjects;
  const hasCompleteMatricRecord = savedSubjects && Object.keys(savedSubjects).length === 7 && Object.hasOwn(savedSubjects, "Life Orientation");
  if (state.profile && hasCompleteMatricRecord) {
    const m = state.profile.marks;
    $("#profile-reminder").textContent = "Your marks profile is ready: seven matric subjects including Life Orientation, APS " + m.aps + ".";
    navigate("courses");
  } else {
    navigate("profile");
    if (state.profile) announce("Update your marks profile with seven subjects, including Life Orientation, before applying.");
  }
}

$("#profile-form").addEventListener("submit", (event) => {
  event.preventDefault();
  if (!event.currentTarget.reportValidity()) return;
  const additionalNames = [4, 5, 6, 7].map((n) => $("#subject-" + n + "-name").value.trim().toLowerCase());
  if (new Set(additionalNames).size !== 4 || additionalNames.some((name) => ["mathematics", "life orientation", "home or first additional language"].includes(name))) {
    return announce("Give each of the four additional subjects a different name. Mathematics, language and Life Orientation are already listed.");
  }
  const candidate = profileFromForm();
  postJson("/api/profile/update", { profile: candidate }).then(async (response) => {
    const data = await response.json();
    if (!response.ok) return announce(data.error || "The profile could not be saved.");
    state.profile = data.profile;
    const m = state.profile.marks;
    $("#profile-reminder").textContent = "Your marks profile is ready: seven matric subjects including Life Orientation, APS " + m.aps + ".";
    navigate("courses");
    announce("Profile saved securely for your account.");
  }).catch(() => announce("Profile could not be saved. Check your secure session and try again."));
});
$("#residence-form").addEventListener("submit", submitResidenceApplication);

$("#delete-account-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!event.currentTarget.reportValidity()) return;
  if (!window.confirm("Permanently delete your UniPath demo account and all associated records? This cannot be undone.")) return;
  const response = await postJson("/api/privacy/delete-account", {
    password: $("#delete-password").value, otp_token: $("#delete-otp").value.trim(),
  });
  const data = await response.json();
  if (!response.ok) return announce(data.error || "The account could not be deleted.");
  window.location.assign("/auth/login/");
});

$("#matches-form").addEventListener("submit", (event) => {
  event.preventDefault();
  renderReview();
  navigate("review");
});
$("#submit-applications").addEventListener("click", submitApplications);
$("#marks-file").addEventListener("change", (event) => {
  const file = event.target.files?.[0];
  $("#file-name").textContent = file ? file.name + " selected. This demo does not read or upload it; enter marks manually." : "No file selected. You can enter marks manually.";
});

$$("[data-page]").forEach((button) => {
  button.addEventListener("click", () => {
    const page = button.dataset.page;
    if (page === "applications") loadApplications();
    if (page === "profile") restoreProfileForm();
    navigate(page);
  });
});

$("#read-aloud").addEventListener("click", () => {
  if (!("speechSynthesis" in window)) return announce("Read aloud is not available in this browser.");
  window.speechSynthesis.cancel();
  const current = $(".page:not(.hidden)");
  const utterance = new SpeechSynthesisUtterance(current?.innerText || "");
  utterance.lang = "en-ZA";
  window.speechSynthesis.speak(utterance);
  announce("Reading the current page aloud.");
});
let textScale = 1;
$("#text-larger").addEventListener("click", () => {
  textScale = Math.min(1.35, textScale + 0.1);
  document.documentElement.style.setProperty("--scale", textScale.toFixed(2));
  announce("Text size " + Math.round(textScale * 100) + " percent.");
});
$("#text-smaller").addEventListener("click", () => {
  textScale = Math.max(0.85, textScale - 0.1);
  document.documentElement.style.setProperty("--scale", textScale.toFixed(2));
  announce("Text size " + Math.round(textScale * 100) + " percent.");
});
$("#contrast-toggle").addEventListener("click", (event) => {
  const enabled = document.body.classList.toggle("high-contrast");
  event.currentTarget.setAttribute("aria-pressed", String(enabled));
  event.currentTarget.innerHTML = '<span aria-hidden="true">◐</span> High contrast: ' + (enabled ? "On" : "Off");
  announce("High contrast " + (enabled ? "on." : "off."));
});

start().catch(() => announce("The demo data could not be loaded. Start the Python app and refresh this page."));
