import { initializeApp } from "https://www.gstatic.com/firebasejs/12.4.0/firebase-app.js";
import { 
  getAuth, 
  onAuthStateChanged, 
  updateEmail 
} from "https://www.gstatic.com/firebasejs/12.4.0/firebase-auth.js";
import { 
  getDatabase, 
  ref, 
  get, 
  update 
} from "https://www.gstatic.com/firebasejs/12.4.0/firebase-database.js";

// Firebase config
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  databaseURL: "YOUR_DATABASE_URL",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Init Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getDatabase(app);

// DOM Elements
const usernameEl = document.getElementById("username");
const fullNameInput = document.getElementById("fullName");
const emailInput = document.getElementById("email");
const orderList = document.getElementById("orderList");
const form = document.getElementById("editProfileForm");

// Check user auth state
onAuthStateChanged(auth, async (user) => {
  if (user) {
    const userRef = ref(db, "users/" + user.uid);
    const snapshot = await get(userRef);
    if (snapshot.exists()) {
      const data = snapshot.val();
      usernameEl.textContent = data.fullName || user.email.split('@')[0];
      fullNameInput.value = data.fullName || "";
      emailInput.value = user.email;
      loadOrderHistory(user.uid);
    } else {
      usernameEl.textContent = user.email.split('@')[0];
    }
  } else {
    alert("Please log in first.");
    window.location.href = "login.html";
  }
});

// Update profile
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const user = auth.currentUser;
  if (user) {
    const name = fullNameInput.value.trim();
    const email = emailInput.value.trim();

    try {
      await updateEmail(user, email);
      await update(ref(db, "users/" + user.uid), {
        fullName: name,
        email: email
      });
      alert("Profile updated successfully!");
    } catch (error) {
      alert("Error updating profile: " + error.message);
    }
  }
});

// Load past orders
async function loadOrderHistory(uid) {
  const ordersRef = ref(db, "orders/" + uid);
  const snapshot = await get(ordersRef);
  orderList.innerHTML = "";

  if (snapshot.exists()) {
    const orders = snapshot.val();
    Object.values(orders).forEach(order => {
      const li = document.createElement("li");
      li.textContent = `${order.item} — ₱${order.total} — ${order.date}`;
      orderList.appendChild(li);
    });
  } else {
    orderList.innerHTML = "<li>No orders found.</li>";
  }
}

// Dummy rating submission
window.submitRating = function () {
  alert("Thanks for rating! (Firebase save can be added here)");
};
