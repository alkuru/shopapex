// JavaScript для админки поставщиков

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация при загрузке страницы
    initializeSupplierAdmin();
});

function initializeSupplierAdmin() {
    // Настройка переключения типа API
    setupAPITypeToggle();
    
    // Настройка кнопок действий
    setupActionButtons();
    
    // Настройка валидации формы
    setupFormValidation();
}

function setupAPITypeToggle() {
    const apiTypeField = document.getElementById('id_api_type');
    if (apiTypeField) {
        toggleAPIFields(apiTypeField.value);
        apiTypeField.addEventListener('change', function() {
            toggleAPIFields(this.value);
        });
    }
}

function toggleAPIFields(apiType) {
    const apiFields = [
        'id_api_url',
        'id_api_login', 
        'id_api_password'
    ];
    
    const isAutoparts = apiType === 'autoparts';
    
    apiFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        const container = field ? field.closest('.form-row, .field-box') : null;
        
        if (container) {
            container.style.display = isAutoparts ? 'block' : 'none';
            
            // Добавляем/убираем required атрибут
            if (field) {
                if (isAutoparts) {
                    field.setAttribute('required', 'required');
                    field.closest('.form-row, .field-box').classList.add('required');
                } else {
                    field.removeAttribute('required');
                    field.closest('.form-row, .field-box').classList.remove('required');
                }
            }
        }
    });
    
    // Показываем/скрываем блок с API настройками
    const apiFieldsGroup = document.querySelector('.api-fields-group');
    if (apiFieldsGroup) {
        apiFieldsGroup.style.display = isAutoparts ? 'block' : 'none';
    }
}

function setupActionButtons() {
    // Кнопка тестирования API
    const testApiBtn = document.querySelector('.test-api-btn');
    if (testApiBtn) {
        testApiBtn.addEventListener('click', function(e) {
            e.preventDefault();
            testAPIConnection(this);
        });
    }
    
    // Кнопки синхронизации
    const syncButtons = document.querySelectorAll('[data-sync-action]');
    syncButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const action = this.getAttribute('data-sync-action');
            performSyncAction(action, this);
        });
    });
}

function setupFormValidation() {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateSupplierForm()) {
                e.preventDefault();
                return false;
            }
        });
    }
}

function validateSupplierForm() {
    const apiType = document.getElementById('id_api_type');
    const apiUrl = document.getElementById('id_api_url');
    const apiLogin = document.getElementById('id_api_login');
    const apiPassword = document.getElementById('id_api_password');
    
    let isValid = true;
    
    // Очищаем предыдущие ошибки
    clearValidationErrors();
    
    if (apiType && apiType.value === 'autoparts') {
        if (!apiUrl || !apiUrl.value.trim()) {
            showValidationError(apiUrl, 'URL API обязателен для типа "autoparts"');
            isValid = false;
        }
        
        if (!apiLogin || !apiLogin.value.trim()) {
            showValidationError(apiLogin, 'Логин API обязателен для типа "autoparts"');
            isValid = false;
        }
        
        // Проверяем пароль только для новых записей
        const isNewRecord = !document.querySelector('input[name="_continue"]');
        if (isNewRecord && (!apiPassword || !apiPassword.value.trim())) {
            showValidationError(apiPassword, 'Пароль API обязателен для нового поставщика');
            isValid = false;
        }
    }
    
    return isValid;
}

function showValidationError(field, message) {
    const container = field.closest('.form-row, .field-box');
    if (container) {
        const errorElement = document.createElement('div');
        errorElement.className = 'validation-error';
        errorElement.style.color = '#dc3545';
        errorElement.style.fontSize = '12px';
        errorElement.style.marginTop = '5px';
        errorElement.textContent = message;
        
        container.appendChild(errorElement);
        field.style.borderColor = '#dc3545';
    }
}

function clearValidationErrors() {
    const errors = document.querySelectorAll('.validation-error');
    errors.forEach(error => error.remove());
    
    const fields = document.querySelectorAll('input, select, textarea');
    fields.forEach(field => {
        field.style.borderColor = '';
    });
}

function testAPIConnection(button) {
    const originalText = button.innerHTML;
    const supplierId = getSupplierIdFromForm();
    
    if (!supplierId) {
        showNotification('Сначала сохраните поставщика', 'error');
        return;
    }
    
    // Показываем индикатор загрузки
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Тестирование...';
    button.disabled = true;
    
    // Выполняем AJAX запрос
    fetch(`/catalog/suppliers/${supplierId}/test_api/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Подключение к API успешно!', 'success');
        } else {
            showNotification(`Ошибка подключения: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при тестировании API', 'error');
    })
    .finally(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

function performSyncAction(action, button) {
    const originalText = button.innerHTML;
    const supplierId = getSupplierIdFromForm();
    
    if (!supplierId) {
        showNotification('Сначала сохраните поставщика', 'error');
        return;
    }
    
    const confirmMessage = getConfirmMessageForAction(action);
    if (!confirm(confirmMessage)) {
        return;
    }
    
    // Показываем индикатор загрузки
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Синхронизация...';
    button.disabled = true;
    
    // Выполняем AJAX запрос
    fetch(`/catalog/suppliers/${supplierId}/${action}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message || 'Синхронизация завершена успешно!', 'success');
        } else {
            showNotification(`Ошибка синхронизации: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при выполнении синхронизации', 'error');
    })
    .finally(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

function getConfirmMessageForAction(action) {
    const messages = {
        'sync_products': 'Вы уверены, что хотите синхронизировать товары? Это может занять некоторое время.',
        'sync_all_entities': 'Вы уверены, что хотите синхронизировать все сущности? Это может занять значительное время.',
        'sync_staff': 'Синхронизировать сотрудников с API?',
        'sync_delivery_methods': 'Синхронизировать методы доставки с API?',
        'sync_order_statuses': 'Синхронизировать статусы заказов с API?',
        'sync_client_groups': 'Синхронизировать группы клиентов с API?',
        'sync_clients': 'Синхронизировать клиентов с API?',
        'sync_orders': 'Синхронизировать заказы с API?'
    };
    
    return messages[action] || 'Вы уверены, что хотите выполнить это действие?';
}

function getSupplierIdFromForm() {
    // Пытаемся получить ID из URL
    const urlParts = window.location.pathname.split('/');
    const changeIndex = urlParts.indexOf('change');
    
    if (changeIndex > 0 && urlParts[changeIndex - 1]) {
        return urlParts[changeIndex - 1];
    }
    
    // Альтернативный способ - из скрытого поля
    const idField = document.querySelector('input[name="id"]');
    if (idField) {
        return idField.value;
    }
    
    return null;
}

function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

function showNotification(message, type = 'info') {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        max-width: 400px;
        word-wrap: break-word;
    `;
    
    // Устанавливаем цвет в зависимости от типа
    const colors = {
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'info': '#17a2b8'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    notification.textContent = message;
    
    // Добавляем на страницу
    document.body.appendChild(notification);
    
    // Автоматически удаляем через 5 секунд
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
    
    // Добавляем возможность закрыть по клику
    notification.addEventListener('click', () => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    });
}
