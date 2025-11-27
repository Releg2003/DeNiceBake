// ✅ Import All Firebase Modules
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.4.0/firebase-app.js";
import { getDatabase, ref, set } from "https://www.gstatic.com/firebasejs/12.4.0/firebase-database.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  sendPasswordResetEmail,
  signOut,
  onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/12.4.0/firebase-auth.js";

/* -------------------------------------------------------------------------- */
/*                             🔹 FIREBASE CONFIG                             */
/* -------------------------------------------------------------------------- */
const firebaseConfig = {
  apiKey: "AIzaSyC6_ACisV2JCAwi1r30uyemtPBVTjEZavk",
  authDomain: "denicebakes.firebaseapp.com",
  databaseURL: "https://denicebakes-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "denicebakes",
  storageBucket: "denicebakes.firebasestorage.app",
  messagingSenderId: "738071187737",
  appId: "1:738071187737:web:4ad5ceb6fb4ee4a7fdf588",
  measurementId: "G-YTTLPMJDSZ"
};

// ✅ Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getDatabase(app);
const auth = getAuth(app);

/* -------------------------------------------------------------------------- */
/*                                  🔹 SIGN UP                                */
/* -------------------------------------------------------------------------- */
window.signupUser = async function (event) {
  event.preventDefault();
  const name = document.getElementById("signupName").value.trim();
  const email = document.getElementById("signupEmail").value.trim();
  const password = document.getElementById("signupPassword").value;

  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    await set(ref(db, "users/" + user.uid), {
      name: name,
      email: email,
      createdAt: new Date().toISOString()
    });

    alert("Account created successfully!");
    switchPopup("signupPopup", "loginPopup");
  } catch (error) {
    alert(error.message);
  }
};

/* -------------------------------------------------------------------------- */
/*                                  🔹 LOGIN                                  */
/* -------------------------------------------------------------------------- */
window.loginUser = async function (event) {
  event.preventDefault();
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  try {
    await signInWithEmailAndPassword(auth, email, password);
    alert("Login successful!");
    closePopup("loginPopup");
  } catch (error) {
    alert(error.message);
  }
};

/* -------------------------------------------------------------------------- */
/*                            🔹 FORGOT PASSWORD                              */
/* -------------------------------------------------------------------------- */
window.forgotPassword = async function (event) {
  event.preventDefault();
  const email = document.getElementById("forgotEmail").value;

  if (!email) {
    alert("Please enter your email address.");
    return;
  }

  try {
    await sendPasswordResetEmail(auth, email);
    alert("Reset link sent! Check your inbox or spam folder.");
    switchPopup("forgotPasswordPopup", "loginPopup");
  } catch (error) {
    alert(error.message);
  }
};

/* -------------------------------------------------------------------------- */
/*                            🔹 AUTH STATE HANDLER                           */
/* -------------------------------------------------------------------------- */
onAuthStateChanged(auth, (user) => {
  if (user) {
    document.getElementById("loginMenu").style.display = "none";
    document.getElementById("logoutMenu").style.display = "inline";
    document.getElementById("orderMenu").style.display = "inline";
    document.getElementById("customMenu").style.display = "inline";
    document.getElementById("userMenu").style.display = "inline";
  } else {
    document.getElementById("loginMenu").style.display = "inline";
    document.getElementById("logoutMenu").style.display = "none";
    document.getElementById("orderMenu").style.display = "none";
    document.getElementById("customMenu").style.display = "none";
    document.getElementById("userMenu").style.display = "none";
  }
});

/* -------------------------------------------------------------------------- */
/*                                  🔹 LOGOUT                                 */
/* -------------------------------------------------------------------------- */
window.logoutUser = async function () {
  try {
    await signOut(auth);
    alert("Logged out successfully!");
    window.location.href = "home.html";
  } catch (error) {
    alert("Error logging out: " + error.message);
  }
};

/* -------------------------------------------------------------------------- */
/*                         🔹 POPUP CONTROL FUNCTIONS                         */
/* -------------------------------------------------------------------------- */
window.openPopup = (id) => document.getElementById(id).style.display = "flex";
window.closePopup = (id) => document.getElementById(id).style.display = "none";
window.switchPopup = (closeId, openId) => {
  closePopup(closeId);
  openPopup(openId);
};
window.openLogin = () => openPopup("loginPopup");
