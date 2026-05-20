const API_BASE_URL = window.API_BASE_URL || 'http://127.0.0.1:8000/api';
const inputBugetMaxim = document.querySelector('#bugetMaxim');
const butonCauta = document.querySelector('#butonCauta');
const containerRezultate = document.querySelector('#rezultateRestaurante');
const mesajGol = document.querySelector('#mesajGol');

function genereazaSlug(numeRestaurant) {
    return numeRestaurant
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .trim()
        .replace(/\s+/g, '-');
}

function construiesteLinkMaps(numeRestaurant, locatieRestaurant) {
    const interogareMaps = encodeURIComponent(`${numeRestaurant} ${locatieRestaurant}`);
    return `https://www.google.com/maps/search/?api=1&query=${interogareMaps}`;
}

function construiesteLinkDetalii(restaurant) {
    const slugRestaurant = restaurant.slug || genereazaSlug(restaurant.nume);
    return `restaurant.html?id=${encodeURIComponent(slugRestaurant)}`;
}

function incarcaRestauranteLocal() {
    if (!Array.isArray(window.restauranteBaiaMare)) {
        return [];
    }

    return window.restauranteBaiaMare.map((restaurant) => ({
        ...restaurant,
        slug: restaurant.slug || genereazaSlug(restaurant.nume),
    }));
}

function obtineLinkRestaurant(restaurant) {
    if (restaurant.linkOficial && restaurant.linkOficial.trim() !== '') {
        return restaurant.linkOficial;
    }

    return construiesteLinkMaps(restaurant.nume, restaurant.locatie);
}

function afiseazaRezultate(restauranteGasite) {
    containerRezultate.innerHTML = '';

    if (restauranteGasite.length === 0) {
        mesajGol.textContent = 'Nu am gasit restaurante pentru filtrul selectat.';
        return;
    }

    mesajGol.textContent = '';

    restauranteGasite.forEach((restaurant) => {
        const linkRestaurant = obtineLinkRestaurant(restaurant);
        const linkDetalii = construiesteLinkDetalii(restaurant);
        const cardRestaurant = document.createElement('article');
        cardRestaurant.className = 'menu-item';

        cardRestaurant.innerHTML = `
            <img class="restaurant-img" src="${restaurant.imagine}" alt="${restaurant.nume}">
            <div class="item-info">
                <h3>${restaurant.nume}</h3>
                <p>Specific: ${restaurant.specific}</p>
                <p>Locatie: ${restaurant.locatie}</p>
                <span class="price">Buget mediu: ${restaurant.buget} RON</span>
                <div class="item-actions">
                    <a class="btn site-btn detalii-btn" href="${linkDetalii}">Detalii</a>
                    <a class="btn site-btn" href="${linkRestaurant}" target="_blank" rel="noopener noreferrer">Viziteaza</a>
                </div>
            </div>
        `;

        containerRezultate.appendChild(cardRestaurant);
    });
}

async function incarcaRestaurante(bugetMaxim) {
    const parametri = new URLSearchParams();
    parametri.set('limit', '500');

    if (typeof bugetMaxim === 'number' && bugetMaxim > 0) {
        parametri.set('max_budget', bugetMaxim.toString());
    }

    const urlApi = `${API_BASE_URL}/restaurants${parametri.toString() ? `?${parametri.toString()}` : ''}`;

    try {
        mesajGol.textContent = 'Se incarca restaurantele...';
        const raspuns = await fetch(urlApi);

        if (!raspuns.ok) {
            throw new Error(`Eroare API: ${raspuns.status}`);
        }

        const restauranteGasite = await raspuns.json();
        afiseazaRezultate(Array.isArray(restauranteGasite) ? restauranteGasite : []);
    } catch (eroare) {
        const restauranteLocale = incarcaRestauranteLocal();
        const rezultateLocale = restauranteLocale.filter((restaurant) => Number(restaurant.buget) <= bugetMaxim);

        if (restauranteLocale.length > 0) {
            afiseazaRezultate(rezultateLocale);
            if (rezultateLocale.length > 0) {
                mesajGol.textContent = '';
            }
            return;
        }

        containerRezultate.innerHTML = '';
        mesajGol.textContent = 'Nu am putut incarca datele din backend sau din fisierul local.';
    }
}

function cautaDupaBuget() {
    const bugetMaxim = Number(inputBugetMaxim.value);

    if (!bugetMaxim || bugetMaxim <= 0) {
        containerRezultate.innerHTML = '';
        mesajGol.textContent = 'Introdu un buget valid.';
        return;
    }

    incarcaRestaurante(bugetMaxim);
}

butonCauta.addEventListener('click', cautaDupaBuget);
inputBugetMaxim.addEventListener('keydown', (eveniment) => {
    if (eveniment.key === 'Enter') {
        cautaDupaBuget();
    }
});

containerRezultate.innerHTML = '';
mesajGol.textContent = 'Introdu un buget si apasa Cauta pentru a vedea restaurantele.';
