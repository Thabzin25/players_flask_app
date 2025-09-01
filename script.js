document.getElementById('loginForm').addEventListener('submit', function(e) {
  e.preventDefault();

  const role = document.getElementById('role').value;
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value.trim();
  const message = document.getElementById('message');

  // Simulated login logic
  if (email === 'admin@scout.com' && password === 'admin123' && role === 'admin') {
    message.style.color = 'green';
    message.textContent = 'Admin login successful!';
    // Redirect logic here
  } else {
    message.style.color = 'red';
    message.textContent = 'Invalid credentials or role.';
  }
});

