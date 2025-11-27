function openLogin() {
  document.getElementById("loginPopup").style.display = "flex";
}

function closePopup(id) {
  document.getElementById(id).style.display = "none";
}

function switchPopup(closeId, openId) {
  document.getElementById(closeId).style.display = "none";
  document.getElementById(openId).style.display = "flex";
}


// Sample users with roles
const users = [
    { email: 'admin@bake.com', password: 'admin123', role: 'admin' },
];

// Store current user in localStorage for session handling
function loginUser(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value.trim();
    const user = users.find(u => u.email === email && u.password === password);

    if (!user) {
        alert("Invalid credentials");
        return false;
    }

    localStorage.setItem('currentUser', JSON.stringify(user));
    alert(`Welcome, ${user.role}!`);

    // Redirect based on role
    switch (user.role) {
        case 'admin':
            window.location.href = 'admin.html';
            break;
        case 'staff':
            window.location.href = 'staff.html';
            break;
        case 'user':
            window.location.href = 'user.html';
            break;
    }

    return false;
}

// Logout and remove user session
function logoutUser() {
    localStorage.removeItem('currentUser');
    alert("Logged out successfully.");
    window.location.href = 'home.html';
}

// Check login state (optional for UI adjustment)
function checkLoginStatus() {
    const user = JSON.parse(localStorage.getItem('currentUser'));
    if (user) {
        document.getElementById("loginMenu").style.display = "none";
        document.getElementById("logoutMenu").style.display = "inline";
        if (user.role === 'user') {
            document.getElementById("orderMenu").style.display = "inline";
            document.getElementById("customMenu").style.display = "inline";
            document.getElementById("userMenu").style.display = "inline";
        }
    }
}


// Open & Close Popup Helpers
function openPopup(id) {
  document.getElementById(id).style.display = "block";
}

function closePopup(id) {
  document.getElementById(id).style.display = "none";
}

function switchPopup(closeId, openId) {
  closePopup(closeId);
  openPopup(openId);
}

// Forgot Password Functionality
function forgotPassword(event) {
  event.preventDefault();

  const email = document.getElementById("forgotEmail").value.trim();

  if (email === "") {
    alert("Please enter your email address.");
    return false;
  }

  // Simulate sending password reset link
  alert(`A password reset link has been sent to ${email}`);

  closePopup('forgotPasswordPopup');
  openPopup('loginPopup');
  return false;
}


// Popup handlers
function openLogin() {
    document.getElementById("loginPopup").style.display = "block";
}

function closePopup(popupId) {
    document.getElementById(popupId).style.display = "none";
}

function switchPopup(hideId, showId) {
    document.getElementById(hideId).style.display = "none";
    document.getElementById(showId).style.display = "block";
}

// Call on pages like home.html to reflect login
window.onload = checkLoginStatus;



