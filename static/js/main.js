/**
 * Lunch Roulette - 繝｡繧､繝ｳJavaScript
 * 繝ｫ繝ｼ繝ｬ繝・ヨ讖溯・縺ｨ繝ｬ繧ｹ繝医Λ繝ｳ陦ｨ遉ｺ縺ｮ繝輔Ο繝ｳ繝医お繝ｳ繝牙・逅・
 */

// DOM隕∫ｴ縺ｮ蜿門ｾ・
const rouletteBtn = document.getElementById('roulette-btn');
const retryBtn = document.getElementById('retry-btn');
const errorMessage = document.getElementById('error-message');
const restaurantSection = document.getElementById('restaurant-section');

// 繝懊ち繝ｳ蜀・・隕∫ｴ
const btnText = rouletteBtn.querySelector('.btn-text');
const btnLoading = rouletteBtn.querySelector('.btn-loading');

// 繝ｬ繧ｹ繝医Λ繝ｳ繧ｫ繝ｼ繝牙・縺ｮ隕∫ｴ
const restaurantName = document.getElementById('restaurant-name');
const restaurantGenre = document.getElementById('restaurant-genre');
const restaurantImage = document.getElementById('restaurant-image');
const restaurantAddress = document.getElementById('restaurant-address');
const restaurantBudget = document.getElementById('restaurant-budget');
const walkingTime = document.getElementById('walking-time');
const restaurantHours = document.getElementById('restaurant-hours');
const restaurantCatch = document.getElementById('restaurant-catch');
const distanceBadge = document.getElementById('distance-badge');
const mapLink = document.getElementById('map-link');
const hotpepperLink = document.getElementById('hotpepper-link');

/**
 * 繝ｭ繝ｼ繝・ぅ繝ｳ繧ｰ迥ｶ諷九・陦ｨ遉ｺ/髱櫁｡ｨ遉ｺ繧貞・繧頑崛縺・
 * @param {boolean} isLoading - 繝ｭ繝ｼ繝・ぅ繝ｳ繧ｰ迥ｶ諷九°縺ｩ縺・°
 */
function toggleLoading(isLoading) {
    if (isLoading) {
        rouletteBtn.disabled = true;
        rouletteBtn.classList.add('loading');
        btnText.style.display = 'none';
        btnLoading.style.display = 'flex';
    } else {
        rouletteBtn.disabled = false;
        rouletteBtn.classList.remove('loading');
        btnText.style.display = 'flex';
        btnLoading.style.display = 'none';
    }
}

/**
 * 繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ縺ｮ陦ｨ遉ｺ
 * @param {string} message - 繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ
 */
function showError(message) {
    const errorText = errorMessage.querySelector('.error-text');
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
    
    // 5遘貞ｾ後↓閾ｪ蜍慕噪縺ｫ髱櫁｡ｨ遉ｺ
    setTimeout(() => {
        hideError();
    }, 5000);
}

/**
 * 繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ縺ｮ髱櫁｡ｨ遉ｺ
 */
function hideError() {
    errorMessage.style.display = 'none';
}

/**
 * 繝ｬ繧ｹ繝医Λ繝ｳ繧ｫ繝ｼ繝峨・陦ｨ遉ｺ
 * @param {Object} data - 繝ｬ繧ｹ繝医Λ繝ｳ繝・・繧ｿ
 */
function displayRestaurant(data) {
    const { restaurant, distance, weather } = data;
    
    // 繝ｬ繧ｹ繝医Λ繝ｳ蝓ｺ譛ｬ諠・ｱ
    restaurantName.textContent = restaurant.name;
    restaurantGenre.textContent = restaurant.genre;
    restaurantAddress.textContent = restaurant.address;
    restaurantBudget.textContent = restaurant.budget_display;
    walkingTime.textContent = distance.time_display;
    restaurantHours.textContent = restaurant.hours || '蝟ｶ讌ｭ譎る俣諠・ｱ縺ｪ縺・;
    restaurantCatch.textContent = restaurant.catch || restaurant.summary || '';
    
    // 霍晞屬繝舌ャ繧ｸ
    distanceBadge.textContent = distance.distance_display;
    
    // 繝ｬ繧ｹ繝医Λ繝ｳ逕ｻ蜒・
    if (restaurant.photo_url && restaurant.photo_url !== 'no-image') {
        restaurantImage.src = restaurant.photo_url;
        restaurantImage.alt = `${restaurant.name}縺ｮ蜀咏悄`;
        restaurantImage.style.display = 'block';
    } else {
        // 繝・ヵ繧ｩ繝ｫ繝育判蜒上∪縺溘・繝励Ξ繝ｼ繧ｹ繝帙Ν繝繝ｼ
        restaurantImage.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPuODrOOCueODiOODqeODs+eUu+WDjzwvdGV4dD48L3N2Zz4=';
        restaurantImage.alt = '繝ｬ繧ｹ繝医Λ繝ｳ逕ｻ蜒上↑縺・;
        restaurantImage.style.display = 'block';
    }
    
    // 繝ｪ繝ｳ繧ｯ險ｭ螳・
    mapLink.href = restaurant.map_url;
    hotpepperLink.href = restaurant.hotpepper_url;
    
    // 繝ｬ繧ｹ繝医Λ繝ｳ繧ｻ繧ｯ繧ｷ繝ｧ繝ｳ繧定｡ｨ遉ｺ
    restaurantSection.style.display = 'block';
    
    // 繧ｹ繝繝ｼ繧ｺ繧ｹ繧ｯ繝ｭ繝ｼ繝ｫ
    restaurantSection.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
    });
    
    console.log('繝ｬ繧ｹ繝医Λ繝ｳ陦ｨ遉ｺ螳御ｺ・', restaurant.name);
}

/**
 * 繝ｬ繧ｹ繝医Λ繝ｳ繧ｻ繧ｯ繧ｷ繝ｧ繝ｳ繧帝撼陦ｨ遉ｺ
 */
function hideRestaurant() {
    restaurantSection.style.display = 'none';
}

/**
 * 繝ｫ繝ｼ繝ｬ繝・ヨ螳溯｡鯉ｼ・JAX騾壻ｿ｡・・
 */
async function executeRoulette() {
    try {
        // 繝ｭ繝ｼ繝・ぅ繝ｳ繧ｰ髢句ｧ・
        toggleLoading(true);
        hideError();
        hideRestaurant();
        
        console.log('繝ｫ繝ｼ繝ｬ繝・ヨ髢句ｧ・..');
        
        // API繝ｪ繧ｯ繧ｨ繧ｹ繝・
        const response = await fetch('/roulette', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        });
        
        // 繝ｬ繧ｹ繝昴Φ繧ｹ蜃ｦ逅・
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // 繧ｨ繝ｩ繝ｼ繝ｬ繧ｹ繝昴Φ繧ｹ縺ｮ蜃ｦ逅・
        if (data.error || !data.success) {
            const errorMsg = data.message || '繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢荳ｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆';
            throw new Error(errorMsg);
        }
        
        // 謌仙粥譎ゅ・蜃ｦ逅・
        if (data.success && data.restaurant) {
            console.log('繝ｫ繝ｼ繝ｬ繝・ヨ謌仙粥:', data);
            displayRestaurant(data);
        } else {
            throw new Error(data.message || '繝ｬ繧ｹ繝医Λ繝ｳ繝・・繧ｿ縺梧ｭ｣縺励￥縺ゅｊ縺ｾ縺帙ｓ');
        }
        
    } catch (error) {
        console.error('繝ｫ繝ｼ繝ｬ繝・ヨ繧ｨ繝ｩ繝ｼ:', error);
        
        // 繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ縺ｮ陦ｨ遉ｺ
        let errorMessage = '繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢荳ｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆';
        
        if (error.message.includes('Failed to fetch')) {
            errorMessage = '繝阪ャ繝医Ρ繝ｼ繧ｯ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆縲ゅう繝ｳ繧ｿ繝ｼ繝阪ャ繝域磁邯壹ｒ遒ｺ隱阪＠縺ｦ縺上□縺輔＞縲・;
        } else if (error.message.includes('HTTP 500')) {
            errorMessage = '繧ｵ繝ｼ繝舌・繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆縲ゅ＠縺ｰ繧峨￥譎る俣繧堤ｽｮ縺・※蜀榊ｺｦ縺願ｩｦ縺励￥縺縺輔＞縲・;
        } else if (error.message.includes('HTTP 429')) {
            errorMessage = '繧｢繧ｯ繧ｻ繧ｹ縺碁寔荳ｭ縺励※縺・∪縺吶ゅ＠縺ｰ繧峨￥譎る俣繧堤ｽｮ縺・※蜀榊ｺｦ縺願ｩｦ縺励￥縺縺輔＞縲・;
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        showError(errorMessage);
        
    } finally {
        // 繝ｭ繝ｼ繝・ぅ繝ｳ繧ｰ邨ゆｺ・
        toggleLoading(false);
    }
}

/**
 * 繝壹・繧ｸ隱ｭ縺ｿ霎ｼ縺ｿ螳御ｺ・凾縺ｮ蛻晄悄蛹・
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Lunch Roulette JavaScript 蛻晄悄蛹門ｮ御ｺ・);
    
    // 繝ｫ繝ｼ繝ｬ繝・ヨ繝懊ち繝ｳ縺ｮ繧ｯ繝ｪ繝・け繧､繝吶Φ繝・
    rouletteBtn.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('繝ｫ繝ｼ繝ｬ繝・ヨ繝懊ち繝ｳ繧ｯ繝ｪ繝・け');
        executeRoulette();
    });
    
    // 蜀阪Ν繝ｼ繝ｬ繝・ヨ繝懊ち繝ｳ縺ｮ繧ｯ繝ｪ繝・け繧､繝吶Φ繝・
    if (retryBtn) {
        retryBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('蜀阪Ν繝ｼ繝ｬ繝・ヨ繝懊ち繝ｳ繧ｯ繝ｪ繝・け');
            executeRoulette();
        });
    }
    
    // 繧ｨ繝ｩ繝ｼ繝｡繝・そ繝ｼ繧ｸ縺ｮ繧ｯ繝ｪ繝・け縺ｧ髱櫁｡ｨ遉ｺ
    errorMessage.addEventListener('click', function() {
        hideError();
    });
    
    // 繧ｭ繝ｼ繝懊・繝峨す繝ｧ繝ｼ繝医き繝・ヨ・・nter繧ｭ繝ｼ縺ｧ繝ｫ繝ｼ繝ｬ繝・ヨ螳溯｡鯉ｼ・
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !rouletteBtn.disabled) {
            e.preventDefault();
            executeRoulette();
        }
    });
    
    console.log('繧､繝吶Φ繝医Μ繧ｹ繝翫・險ｭ螳壼ｮ御ｺ・);
});

/**
 * 繝壹・繧ｸ髮｢閼ｱ譎ゅ・蜃ｦ逅・
 */
window.addEventListener('beforeunload', function() {
    // 騾ｲ陦御ｸｭ縺ｮ繝ｪ繧ｯ繧ｨ繧ｹ繝医′縺ゅｋ蝣ｴ蜷医・隴ｦ蜻奇ｼ医が繝励す繝ｧ繝ｳ・・
    if (rouletteBtn.disabled) {
        return '繝ｬ繧ｹ繝医Λ繝ｳ讀懃ｴ｢荳ｭ縺ｧ縺吶ゅ・繝ｼ繧ｸ繧帝屬繧後∪縺吶°・・;
    }
});

/**
 * 繧ｨ繝ｩ繝ｼ繝上Φ繝峨Μ繝ｳ繧ｰ - 譛ｪ蜃ｦ逅・・繧ｨ繝ｩ繝ｼ繧偵く繝｣繝・メ
 */
window.addEventListener('error', function(e) {
    console.error('JavaScript 繧ｨ繝ｩ繝ｼ:', e.error);
    showError('莠域悄縺励↑縺・お繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆縲ゅ・繝ｼ繧ｸ繧貞・隱ｭ縺ｿ霎ｼ縺ｿ縺励※縺上□縺輔＞縲・);
});

/**
 * Promise 縺ｮ譛ｪ蜃ｦ逅・お繝ｩ繝ｼ繧偵く繝｣繝・メ
 */
window.addEventListener('unhandledrejection', function(e) {
    console.error('譛ｪ蜃ｦ逅・・Promise繧ｨ繝ｩ繝ｼ:', e.reason);
    showError('騾壻ｿ｡繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆縲ゅ＠縺ｰ繧峨￥譎る俣繧堤ｽｮ縺・※蜀榊ｺｦ縺願ｩｦ縺励￥縺縺輔＞縲・);
    e.preventDefault();
});