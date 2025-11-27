let cart = [];

function addToCart(name, price, size) {
  // Add item to cart array
  cart.push({ name, price, size });
  renderCart();
}

function removeFromCart(index) {
  cart.splice(index, 1); // remove the selected item
  renderCart();
}

function renderCart() {
  const cartItems = document.getElementById('cartItems');
  const totalPriceEl = document.getElementById('totalPrice');
  cartItems.innerHTML = '';
  let total = 0;

  cart.forEach((item, index) => {
    total += item.price;

    const div = document.createElement('div');
    div.classList.add('cart-item');
    div.innerHTML = `
      <p><strong>${item.name}</strong> (${item.size}) - $${item.price}</p>
      <button class="remove-btn" onclick="removeFromCart(${index})">Remove</button>
    `;
    cartItems.appendChild(div);
  });

  totalPriceEl.textContent = total.toFixed(2);
}

function submitOrder() {
  if (cart.length === 0) {
    alert("Your cart is empty!");
    return;
  }
  alert("Order placed successfully! 🎉");
  cart = [];
  renderCart();
}
