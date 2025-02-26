
document.addEventListener("DOMContentLoaded", () => {
   
    sidebar();
    fetchAndUpdateData();
});

function sidebar() {
    // Get the elements
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sideoverlay');
    const mainContent = document.getElementById('main-content');
    const barmenu = document.getElementById('hamburger-menu');
    const barmenulogo = document.getElementById('logo');

    // Function to open the sidebar
    function openSidebar() {
        sidebar.classList.add('open');
        overlay.style.display = 'block';
        mainContent.classList.add('blurred');
        
    }

    // Function to close the sidebar
    function closeSidebar() {
        sidebar.classList.remove('open');
        overlay.style.display = 'none';
        mainContent.classList.remove('blurred');
        
    }

    // Function to handle the active tab highlighting
    function activeTab() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', function() {
                document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    
    
     // Event listener for the overlay
     overlay.addEventListener('click', closeSidebar);
    // Add event listener to open sidebar button
    document.getElementById('hamburger-menu').addEventListener('click', openSidebar);
}


function fetchAndUpdateData() {
    const container = document.getElementById('main-content');
    const fragment = document.createDocumentFragment(); // Create a DocumentFragment for batching

    fetch('http://localhost:5000/api/get-data', { method: 'GET' })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            container.innerHTML = ''; // Clear existing content

            data.forEach(row => {
                const rowDiv = document.createElement('div');

                // Format the date
                const formattedDate = formatDate(row.exdate);

                rowDiv.className = 'product';
                rowDiv.setAttribute('data-id', row.id);
                rowDiv.setAttribute('data-name', row.product_name);
                rowDiv.setAttribute('data-stock', row.stock);
                rowDiv.setAttribute('data-unit', row.unit);
                rowDiv.setAttribute('data-expiration', formattedDate);
                rowDiv.setAttribute('data-barcode', row.barcode);
                rowDiv.setAttribute('data-price', row.price);
                rowDiv.setAttribute('data-priceper', row.per);
                rowDiv.setAttribute('data-image', row.image_path || '');

                // Use lazy loading for images
                const imgElement = row.image_path
                    ? `<img src="http://localhost:5000${row.image_path}" alt="${row.product_name}" loading="lazy">`
                    : '';

                // Pre-calculate stock and expiration information
                // const stockInfoContent = getStockAndExpirationInfo(row.stock, row.unit, formattedDate);

                rowDiv.innerHTML = `
                    ${imgElement}
                    <h2 style="color: blue">${row.product_name}</h2>
                    <p style="color: lime">ETB ${row.price} ${row.per}</p>
                    <div class="cart-info">
                        <input id='quanin' type="number" placeholder='Quantity'  min="1" max="${row.stock}" style="width: 50px; margin-right: 10px;">
                        <button class="add-to-cart" onclick="addToCart(this)">Add to Cart</button>
                    </div>
                `;

                fragment.appendChild(rowDiv); // Append to the DocumentFragment
            });

            container.appendChild(fragment); // Append the DocumentFragment to the DOM in one operation
        })
        .catch(error => {
            console.error('Error fetching data:', error.message || error);
            alert('Failed to load data. Please try again later.');
        });
}

// Helper function to format dates

let acc = 0;
const cart = [];

function addToCart(button) {
    const product = button.closest('.product');
    const productId = product.getAttribute('data-id');
    const productName = product.getAttribute('data-name');
    const productPrice = parseFloat(product.getAttribute('data-price')); // Convert to number
    const productUnit = product.getAttribute('data-priceper');

    const quan = parseFloat(product.querySelector('input').value) || 0; // Ensure it's a number

    // Ensure quantity is valid before adding
    if (quan <= 0) {
        alert("Please enter a valid quantity.");
        return;
    }

    // Add the product to the cart array
    cart.push({
        id: productId,
        name: productName,
        unit: productUnit,
        price: productPrice,
        quantity: quan
    });

    console.table(cart);

    const newRow = document.createElement('tr');
    const total = document.getElementById('total');
    const cartTable = document.getElementById('tbody');

    let productPriceg = productPrice;
    if (productUnit === '100g' || productUnit === '/100g' || productUnit === '/ 100g') {
        productPriceg = productPrice * 10; // Convert price per 100g to per 1kg
    }

    const subtotal = productPriceg * quan;

    newRow.innerHTML = `
        <td><input type="checkbox" class='cart-checkbox'></td>
        <td>${productName}</td>
        <td>${quan} ${productUnit}</td>
        <td>${productPriceg.toLocaleString()} birr</td>
        <td class='subtotal'>${subtotal.toLocaleString()} birr</td>
    `;

    cartTable.appendChild(newRow);
    product.querySelector('input').value = ''; // Clear input field

    acc += subtotal;
    total.textContent = acc.toLocaleString() + ' birr';

    // Scroll to the bottom of the table
    let tableWrapper = document.querySelector('.table-wrapper');
    tableWrapper.scrollTop = tableWrapper.scrollHeight;



    // Attach event listener to toggle clear button visibility
    newRow.querySelector(".cart-checkbox").addEventListener("change", toggleClearButton);
    

    
}

function checkout () {
    if(cart.length !== 0) {
        alert('Thank you for shopping with us. Your order has been placed successfully.');
    }
    else {
        alert('Your cart is empty. Please add items to your cart before checking out.');
    }
}

// ** Clear selected items from the cart **
function clearCheckedItems() {
    const checkboxes = document.querySelectorAll('.cart-checkbox:checked');
    const clearButton = document.getElementById('clear-btn');
    const checkAll = document.getElementById('selectAllCheckbox');
    let total = document.getElementById('total');
    



    //alert('Are you sure you want to remove the selected items?');
    checkboxes.forEach((checkbox) => {
        let row = checkbox.closest('tr');
        let subtotalText = row.querySelector('.subtotal').textContent;
        let subtotal = parseFloat(subtotalText.replace(/[^0-9.]/g, "")); // Convert to number

        // Remove from the total amount
        acc -= subtotal;
        row.remove();

    });

    checkAll.checked = false;
    clearButton.style.display = "none";
    checkAll.style.display = "none";
    total.textContent = acc.toLocaleString() + ' birr';
    
}

document.getElementById('selectAllCheckbox').addEventListener('change', function () {
    const checkboxes = document.querySelectorAll('.cart-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
    });
    

});




// ** Show/Hide Clear Button based on selection **
function toggleClearButton() {
    const checkboxes = document.querySelectorAll('.cart-checkbox:checked');
    const clearButton = document.getElementById('clear-btn');
    const checkAll = document.getElementById('selectAllCheckbox');

    if (checkboxes.length > 0) {
        clearButton.style.display = "block";
        checkAll.style.display = "block";
    } else {
        clearButton.style.display = "none";
        checkAll.style.display = "none";

    }
    
    //alert(`made it to here ${checkboxes.length}`);
}










function searchProducts() {
    const searchBar = document.querySelector('.search-bar input');
    const searchTerm = searchBar.value.toLowerCase().trim();
    const products = document.querySelectorAll('.product');

    products.forEach(product => {
        const productName = product.querySelector('h2').textContent.toLowerCase();
        product.style.display = !searchTerm || productName.includes(searchTerm) ? 'block' : 'none';
    });
}

// Add event listener for keypress on the search input
const searchInput = document.querySelector('.search-bar input');
searchInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevent the default form submission
        searchProducts(); // Call the search function
    }
});

 // Show clear button when there is text in the input
 searchInput.addEventListener('input', function () {
    if (this.value.length > 0) {
        clearButton.style.display = 'block';
    } else {
        clearButton.style.display = 'none';
    }
});
 // Clear input when the button is clicked
 clearButton.addEventListener('click', function () {
    searchInput.value = '';
    clearButton.style.display = 'none';
    searchProducts(); // Clear the search results
    searchInput.focus();
});

// Add this function to format the date
function formatDate(dateString) {
    // Current implementation doesn't handle invalid dates
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
        return 'Invalid Date';
    }
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = String(date.getFullYear());
    return `${year}-${month}-${day}`;
}

// Initial fetch


// Set up polling every 5 seconds (5000 milliseconds)
 //setInterval(fetchAndUpdateData, 5000);

