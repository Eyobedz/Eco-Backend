
document.addEventListener("DOMContentLoaded", () => {
   
    sidebar();
    fetchAndUpdateData();
    storedValue();
});

const notifier = new ToastNotification();

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
    const noResult = document.getElementById('no-result');
    
    noResult.style.display = 'none';

    GearboxLoader.show();
  
    
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
            view();
        })
        .catch(error => {
            console.error('Error fetching data:', error.message || error);
            // alert('Failed to load data. Please try again later.');
            notifier.error('Failed to load data. Please try again later.', 3000);

        })

        .finally(() => {
            // Hide loader after fetching data (success or error)
            GearboxLoader.hide();
            noResult.style.display = 'block';

           
        });
}


function fetchFilterData() {
    fetch('http://localhost:5000/api/get-filter', { method: 'GET' })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        document.querySelector('.category-options ul').innerHTML = ``;
        document.querySelector('.unit-options ul').innerHTML = ``;

        catagory = [];
        unit = [];
        data.forEach(row => {
            if (!catagory.includes(row.catagory)){
                catagory.push(row.catagory);

                document.querySelector('.category-options ul').innerHTML += `<li><label><input type="checkbox" class="filter-checkbox" value="${row.catagory}">${row.catagory}</label></li>`;
            }

            if (!unit.includes(row.unit)){
                unit.push(row.unit);

                document.querySelector('.unit-options ul').innerHTML += `<li><label><input type="checkbox" class="filter-checkbox" value="${row.unit}">${row.unit}</label></li>`;
            }
        });
        // alert('Data fetched successfully');
        // console.log(catagory, unit);
        })
    .catch(error => {
        console.error('Error fetching data:', error.message || error);
        // alert('Failed to load data. Please try again later.');
        // notifier.error('Failed to load data. Please try again later.');

    })

//    .finally(() => {
//         // Hide loader after fetching data (success or error)
//         GearboxLoader.hide();
//          //loader.style.display = 'none';
//     });

}

function clearFilter() {
document.querySelectorAll('.filter-options input[type="checkbox"]').forEach(input => input.checked = false);
// filterProducts();
}

function filterProducts() {
const products = document.querySelectorAll('.product');

const selectedStock = Array.from(document.querySelectorAll('.stock-options input[type="checkbox"]:checked'))
.map(option => option.value);

const selectedExpiration = Array.from(document.querySelectorAll('.expire-options input[type="checkbox"]:checked'))
.map(option => option.value);

const selectedUnits = Array.from(document.querySelectorAll('.unit-options input[type="checkbox"]:checked'))
.map(option => option.value);

const selectedCatagory = Array.from(document.querySelectorAll('.category-options input[type="checkbox"]:checked'))
.map(option => option.value);

products.forEach(product => {
let isVisible = true;

// Stock Filter
const stock = Number(product.getAttribute('data-stock'));
if (selectedStock.length > 0) {
    if (selectedStock.includes('instock') && stock > 0) {
        // Keep it visible
    } else if (selectedStock.includes('outstock') && stock === 0) {
        // Keep it visible
    } else if (selectedStock.includes('lowstock') && stock > 0 && stock < 10) {
        // Keep it visible
    } else {
        isVisible = false;
    }
}

// Expiration Filter
const expirationDate = new Date(product.getAttribute('data-expiration'));
const today = new Date();
const daysToExpire = Math.ceil((expirationDate - today) / (1000 * 3600 * 24));
if (selectedExpiration.length > 0) {
    if (selectedExpiration.includes('expired') && daysToExpire <= 0) {
        // Keep it visible
        // product.style.backgroundColor = 'rgba(255, 0, 0, 0.5)';
    } else if (selectedExpiration.includes('expiring') && daysToExpire <= 7 && daysToExpire > 0) {
        // Keep it visible
        // product.style.backgroundColor = 'orange';

    } else {
        isVisible = false;
    }
}

// Unit Filter
const productUnit = product.getAttribute('data-unit');
if (selectedUnits.length > 0 && !selectedUnits.includes(productUnit)) {
    isVisible = false;
}

// categor Filter
const productCatagory = product.getAttribute('data-catagory');
if (selectedCatagory.length > 0 && !selectedCatagory.includes(productCatagory)) {
    isVisible = false;
    // console.log('made it here');
}
let dis
if (localStorage.getItem("selectedView")==='list') {
    dis = 'grid';
} else {
    dis = 'block';
}

// Apply final visibility
product.style.display = isVisible ? dis : 'none';
});
document.getElementById('filterMenu').hidePopover();
view();
}

// document.addEventListener('change', function(event) {
//     if (event.target.matches('.filter-options input[type="checkbox"]')) {
//         filterProducts();
//     }
// });



function storedValue() {
const ViewRadios = document.querySelectorAll('input[name="view"]');
const SortRadios = document.querySelectorAll('input[name="sort"]');

const storedView = localStorage.getItem("selectedView");
const storedSort = localStorage.getItem("selectedSort");

// Restore saved value
if (storedView) {
ViewRadios.forEach(radio => {
    if (radio.value === storedView) {
        radio.checked = true;
    }
});
}

// Save selected value
ViewRadios.forEach(radio => {
radio.addEventListener("change", function () {
    localStorage.setItem("selectedView", this.value);
});
});
console.log('storedValue', storedView);

// Restore saved value
if (storedSort) {
SortRadios.forEach(radio => {
    if (radio.value === storedSort) {
        radio.checked = true;
    }
});
}

// Save selected value
SortRadios.forEach(radio => {
radio.addEventListener("change", function () {
    localStorage.setItem("selectedSort", this.value);
});
});
console.log('storedSort', storedSort);
}

function view() {
if (localStorage.getItem("selectedView") === 'list') {


document.querySelectorAll('.products .product').forEach(function(element) {
    element.classList.add('list-view');
    element.classList.remove('grid-view');
});


} else {

document.querySelectorAll('.products .product').forEach(function(element) {
    element.classList.add('grid-view');
    element.classList.remove('list-view');
});


}
}


function sort (){

}


// Helper function to format dates
let acc = 0;
const cart = [];

function addToCart(button) {
    const product = button.closest('.product');
    const productId = product.getAttribute('data-id');
    const productName = product.getAttribute('data-name');
    const productPrice = parseFloat(product.getAttribute('data-price'));
    const productUnit = product.getAttribute('data-priceper'); // e.g., '100g' or 'kg'
    let quan = Math.abs(parseFloat(product.querySelector('input').value)) || 0; // Ensure valid quantity

    

    if (quan <= 0) {
        notifier.error('Please enter a valid quantity.');
        return;
    }

    if (quan > parseFloat(product.getAttribute('data-stock'))) {
        notifier.error('The quantity you entered is more than the available stock.');
        return;
    }

    // Convert price if product is sold per 100g
    let productPricePerGram = productPrice;
    if (productUnit.includes('100g')) {
        productPricePerGram = productPrice / 100; // Convert price per 100g to per gram
    }

    let subtotal = productPricePerGram * quan;

    // Check if product already exists in the cart array
    let existingProduct = cart.find(item => item.id === productId);

    if (existingProduct) {
        // Update quantity and subtotal
        existingProduct.quantity += quan;
        existingProduct.subtotal = existingProduct.quantity * productPricePerGram;
    } else {
        // Add new product to cart
        cart.push({
            date: document.getElementById('cart-date').value,
            id: productId,
            name: productName,
            price: productPricePerGram,
            unit: productUnit,
            quantity: quan,
            subtotal: subtotal
        });
    }

    
    // Update the displayed cart table
    updateCartTable();
}

function updateCartTable() {
    const cartTable = document.getElementById('tbody');
    const total = document.getElementById('total');
    cartTable.innerHTML = ''; // Clear existing rows
    acc = 0; // Reset total

    cart.forEach(product => {
        const newRow = document.createElement('tr');
        newRow.setAttribute("data-id", product.id);

        newRow.innerHTML = `
            <td><input type="checkbox" class='cart-checkbox'></td>
            <td>${product.name}</td>
            <td class="quantity">${product.quantity} ${product.unit}</td>
            <td>${product.price.toFixed(2)} birr</td>
            <td class='subtotal'>${product.subtotal.toFixed(2)} birr</td>
        `;

        cartTable.appendChild(newRow);
        newRow.querySelector(".cart-checkbox").addEventListener("change", toggleClearButton);

        acc += product.subtotal;
    });

    total.textContent = acc.toLocaleString() + ' birr';
}



document.addEventListener("DOMContentLoaded", function () {
    let today = new Date().toISOString().split('T')[0]; // Get today's date in YYYY-MM-DD format
    document.getElementById("cart-date").value = today;
  });

async function checkout () {
    
    try {
        const formData = cart.map(product => {
            return {
                id: product.id,
                quantity: product.quantity,
                price: product.price,
                date: product.date
            };
        });

        const jsonData = JSON.stringify(formData);
        console.log(jsonData);

        if (jsonData === '[]') {
            // alert('Your cart is empty. Please add items to your cart before checking out.');
            notifier.error('Your cart is empty. Please add items to your cart before checking out.');
            return;
        }
        else {
            // Make sure this URL matches your Flask route exactly
            const response = await fetch('http://localhost:5000/api/add-to-cart', {  // Updated URL
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'  // Ensure the server knows you're sending JSON
                },
                body: jsonData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            document.querySelector("#carttable tbody").innerHTML = "";
            document.querySelector("#total").innerHTML = "0";
            cart.length = 0;

            console.log('Success:', data);
            // alert('Checkout successfully!');
            notifier.success('Checkout successfully!');

        
        // document.getElementById('message').textContent = 'Product added successfully!';
            //document.getElementById('product-form').reset();
        }
    } 
    catch (error) {
        console.error('Error:', error);
        // alert('Error Checking out. Please try again.');
        notifier.error('Error Checking out. Please try again.');

        // document.getElementById('message').textContent = 'Error Checking out. Please try again.';
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
        console.log(row);
        let subtotalText = row.querySelector('.subtotal').textContent;
        let subtotal = parseFloat(subtotalText.replace(/[^0-9.]/g, "")); // Convert to number
        let rowIndex = parseInt(row.getAttribute('data-index'), 10);        
        acc -= subtotal; // Remove from the total amount
        
        
        console.log(rowIndex);
        cart.splice(rowIndex, 1)
        // console.table(cart);

        // // Remove the item from the cart array based on the row index
   
        row.remove();
       
    });

    console.table(cart);

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
        let dis
        if (localStorage.getItem("selectedView")==='list') {
            dis = 'grid';
        } else {
            dis = 'block';
        }
        const productName = product.querySelector('h2').textContent.toLowerCase();
        product.style.display = !searchTerm || productName.includes(searchTerm) ? dis : 'none';
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

