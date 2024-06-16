// static/js/scripts.js
let selectedPharmacy = null;
let selectedProduct = null;

function fetchRegions() {
    fetch('http://localhost:8081/regions')
        .then(response => response.json())
        .then(data => {
            let regionSelect = document.getElementById('region-select');
            regionSelect.innerHTML = '<option value="">Select a region</option>';
            data.regions.forEach(region => {
                let option = document.createElement('option');
                option.value = region.code;
                option.text = region.name;
                regionSelect.add(option);
            });
        })
        .catch(error => console.error('Error fetching regions:', error));
}

document.getElementById('region-select').addEventListener('change', function() {
    let regionCode = this.value;
    fetch(`http://localhost:8081/regions/${regionCode}/provinces`)
        .then(response => response.json())
        .then(data => {
            let provinceSelect = document.getElementById('province-select');
            provinceSelect.innerHTML = '<option value="">Select a province</option>';
            data.provinces.forEach(province => {
                let option = document.createElement('option');
                option.value = province.name;
                option.text = province.name;
                provinceSelect.add(option);
            });
        })
        .catch(error => console.error('Error fetching provinces:', error));
});

document.getElementById('province-select').addEventListener('change', function() {
    let regionCode = document.getElementById('region-select').value;
    let provinceName = this.value;
    fetch(`http://localhost:8081/regions/${regionCode}/provinces/${provinceName}/cities`)
        .then(response => response.json())
        .then(data => {
            let citySelect = document.getElementById('city-select');
            citySelect.innerHTML = '<option value="">Select a city</option>';
            data.cities.forEach(city => {
                let option = document.createElement('option');
                option.value = city.name;
                option.text = city.name;
                citySelect.add(option);
            });
        })
        .catch(error => console.error('Error fetching cities:', error));
});

document.getElementById('submit-btn').addEventListener('click', function() {
    let regionCode = document.getElementById('region-select').value;
    let provinceName = document.getElementById('province-select').value;
    let cityName = document.getElementById('city-select').value;
    fetch(`http://localhost:8081/regions/${regionCode}/provinces/${provinceName}/cities/${cityName}/pharmacies`)
        .then(response => response.json())
        .then(data => {
            let tableBody = document.getElementById('pharmacies-table-body');
            tableBody.innerHTML = '';
            data.pharmacies.forEach(pharmacy => {
                let row = document.createElement('tr');
                row.innerHTML = `
                    <td><input type="radio" name="pharmacy" value="${pharmacy.address}, ${pharmacy.city}" onchange="selectPharmacy(this)"></td>
                    <td>${pharmacy.name}</td>
                    <td>${pharmacy.address}</td>
                    <td>${pharmacy.cap}</td>
                    <td>${pharmacy.city}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching pharmacies:', error));
});

function selectPharmacy(radio) {
    selectedPharmacy = radio.value;
}

document.getElementById('search-product-btn').addEventListener('click', function() {
    let productName = document.getElementById('product-name-input').value;
    fetch(`http://localhost:8081/search-product?product_name=${productName}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Product not found');
            }
            return response.json();
        })
        .then(data => {
            let productDetailsTableBody = document.getElementById('product-details');
            productDetailsTableBody.innerHTML = '';
            if (data.error) {
                let row = document.createElement('tr');
                let cell = document.createElement('td');
                cell.colSpan = 3;
                cell.style.color = 'red';
                cell.textContent = data.error;
                row.appendChild(cell);
                productDetailsTableBody.appendChild(row);
            } else {
                selectedProduct = productName;
                let productDetails = data.details;
                productDetails.forEach(detail => {
                    let row = document.createElement('tr');
                    let selectCell = document.createElement('td');
                    let selectInput = document.createElement('input');
                    selectInput.type = 'radio';
                    selectInput.name = 'product';
                    selectInput.value = detail.description + ' - ' + detail.commercial_code;
                    selectInput.onchange = selectProduct;
                    selectCell.appendChild(selectInput);
                    let descriptionCell = document.createElement('td');
                    let commercialCodeCell = document.createElement('td');
                    descriptionCell.textContent = detail.description;
                    commercialCodeCell.textContent = detail.commercial_code;
                    row.appendChild(selectCell);
                    row.appendChild(descriptionCell);
                    row.appendChild(commercialCodeCell);
                    productDetailsTableBody.appendChild(row);
                });
            }
        })
        .catch(error => {
            let productDetailsTableBody = document.getElementById('product-details');
            productDetailsTableBody.innerHTML = '';
            let row = document.createElement('tr');
            let cell = document.createElement('td');
            cell.colSpan = 3;
            cell.style.color = 'red';
            cell.textContent = error.message;
            row.appendChild(cell);
            productDetailsTableBody.appendChild(row);
        });
});

function selectProduct(event) {
    const ticket = document.createElement('div');
    ticket.classList.add('ticket');
    ticket.textContent = `Selected Product: ${event.target.value}`;
    document.querySelector('.form-section').appendChild(ticket);
}

document.getElementById('get-directions-btn').addEventListener('click', function() {
    let currentLocation = document.getElementById('current-location').value;
    if (!currentLocation || !selectedPharmacy) {
        alert('Please select a pharmacy and enter your current location.');
        return;
    }
    geocodeAddress(currentLocation, function(startCoords) {
        geocodeAddress(selectedPharmacy, function(endCoords) {
            initMap(startCoords, endCoords);
        });
    });
});

function geocodeAddress(address, callback) {
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${address}`)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                let coords = {
                    lat: parseFloat(data[0].lat),
                    lon: parseFloat(data[0].lon)
                };
                callback(coords);
            } else {
                alert('Address not found: ' + address);
            }
        })
        .catch(error => console.error('Error geocoding address:', error));
}

function initMap(startCoords, endCoords) {
    let map = L.map('map').setView([startCoords.lat, startCoords.lon], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    L.Routing.control({
        waypoints: [
            L.latLng(startCoords.lat, startCoords.lon),
            L.latLng(endCoords.lat, endCoords.lon)
        ],
        routeWhileDragging: true
    }).addTo(map);
}

function sortTable(columnIndex) {
    const table = document.getElementById("pharmacies-table-body");
    const rows = Array.from(table.getElementsByTagName("tr"));
    const sortedRows = rows.sort((a, b) => {
        const cellA = a.getElementsByTagName("td")[columnIndex].innerText.toLowerCase();
        const cellB = b.getElementsByTagName("td")[columnIndex].innerText.toLowerCase();
        return cellA.localeCompare(cellB);
    });
    table.innerHTML = "";
    sortedRows.forEach(row => table.appendChild(row));
}

document.getElementById('search-pharmacy').addEventListener('input', function() {
    const filter = this.value.toLowerCase();
    const rows = document.querySelectorAll('#pharmacies-table-body tr');
    rows.forEach(row => {
        const address = row.getElementsByTagName('td')[2].innerText.toLowerCase();
        const zip = row.getElementsByTagName('td')[3].innerText.toLowerCase();
        if (address.includes(filter) || zip.includes(filter)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});

fetchRegions();
