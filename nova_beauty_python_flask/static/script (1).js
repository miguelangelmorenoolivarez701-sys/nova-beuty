// ====================== //
//  FUNCIONES DEL CARRITO //
// ====================== //
let cart = [];

function addToCart(name, price) {
  const item = cart.find(p => p.name === name);
  if (item) {
    item.qty++;
  } else {
    cart.push({ name, price, qty: 1 });
  }
  updateCart();
}

function removeFromCart(name) {
  cart = cart.filter(p => p.name !== name);
  updateCart();
}

function clearCart() {
  cart = [];
  updateCart();
}

function updateCart() {
  const cartTableBody = document.querySelector("#cart-table tbody");
  const cartCount = document.getElementById("cart-count");
  const cartTotal = document.getElementById("cart-total");
  const kpiCart = document.getElementById("kpi-cart");
  const kpiTotal = document.getElementById("kpi-total");

  cartTableBody.innerHTML = "";
  let total = 0;
  let count = 0;

  cart.forEach(item => {
    const subtotal = item.qty * item.price;
    total += subtotal;
    count += item.qty;

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.name}</td>
      <td>${item.qty}</td>
      <td>$${item.price.toLocaleString()}</td>
      <td>$${subtotal.toLocaleString()}</td>
      <td><button class="btn danger" onclick="removeFromCart('${item.name}')">Eliminar</button></td>
    `;
    cartTableBody.appendChild(row);
  });

  cartCount.textContent = count;
  cartTotal.textContent = `$${total.toLocaleString()}`;
  if (kpiCart) kpiCart.textContent = count;
  if (kpiTotal) kpiTotal.textContent = `$${total.toLocaleString()}`;
}

// ====================== //
//   FILTROS DE PRODUCTOS //
// ====================== //
function filterProducts() {
  const query = document.getElementById("q").value.toLowerCase();
  const cat = document.getElementById("cat").value;

  const products = document.querySelectorAll(".product");
  products.forEach(p => {
    const name = p.dataset.name.toLowerCase();
    const category = p.dataset.cat;
    const matchesName = name.includes(query);
    const matchesCat = !cat || category === cat;

    if (matchesName && matchesCat) {
      p.style.display = "block";
    } else {
      p.style.display = "none";
    }
  });
}

// =====================
// REGISTRO
// =====================
function handleRegister(event) {
  event.preventDefault();

  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!name || !email || !password) {
    alert("Por favor, completa todos los campos.");
    return;
  }

  // Guardar datos en localStorage
  const user = { name, email, password };
  localStorage.setItem("user", JSON.stringify(user));

  alert("Registro exitoso 🎉. Ahora inicia sesión.");
  window.location.href = "iniciarsesion.html"; // redirigir a iniciar sesión
}

// =====================
// LOGIN
// =====================
function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  const storedUser = JSON.parse(localStorage.getItem("user"));

  if (!storedUser) {
    alert("No hay usuarios registrados. Por favor, regístrate primero.");
    window.location.href = "registro.html";
    return;
  }

  if (storedUser.email === email && storedUser.password === password) {
    alert("Inicio de sesión exitoso ✅ Bienvenido " + storedUser.name);
    localStorage.setItem("loggedIn", "true"); // marcar sesión activa
    window.location.href = "pagina del proyecto.html"; // redirigir a la página principal
  } else {
    alert("Correo o contraseña incorrectos ❌");
  }
}

// =====================
// CERRAR SESIÓN (opcional)
// =====================
function logout() {
  localStorage.removeItem("loggedIn");
  alert("Sesión cerrada 👋");
  window.location.href = "iniciarsesion.html";
}

// =====================
// VERIFICAR SESIÓN EN INDEX
// =====================
function checkAuth() {
  const loggedIn = localStorage.getItem("loggedIn");
  if (!loggedIn) {
    window.location.href = "iniciarsesion.html";
  }
}


document.addEventListener("DOMContentLoaded", () => {
  const year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();
});

function scrollToSection(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({behavior: "smooth"});
}
