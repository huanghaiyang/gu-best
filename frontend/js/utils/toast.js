import { createApp, ref } from 'vue';
import Toast from '../components/toast.vue';

const toastContainer = ref(null);
const toastInstances = ref([]);

const createToastContainer = () => {
    if (toastContainer.value) return;
    
    const container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
    toastContainer.value = container;
};

const show = (message, options = {}) => {
    createToastContainer();
    
    const {
        type = 'info',
        duration = 3000,
        position = 'top-right'
    } = options;
    
    const toastApp = createApp(Toast, {
        message,
        type,
        duration,
        position,
        onClose: () => {
            removeToast(toastApp);
        }
    });
    
    const toastElement = document.createElement('div');
    toastContainer.value.appendChild(toastElement);
    toastApp.mount(toastElement);
    
    toastInstances.value.push({
        app: toastApp,
        element: toastElement
    });
    
    return toastApp;
};

const removeToast = (toastApp) => {
    const index = toastInstances.value.findIndex(item => item.app === toastApp);
    if (index > -1) {
        const instance = toastInstances.value[index];
        instance.app.unmount();
        instance.element.remove();
        toastInstances.value.splice(index, 1);
    }
};

const success = (message, options = {}) => {
    return show(message, { ...options, type: 'success' });
};

const error = (message, options = {}) => {
    return show(message, { ...options, type: 'error' });
};

const warning = (message, options = {}) => {
    return show(message, { ...options, type: 'warning' });
};

const info = (message, options = {}) => {
    return show(message, { ...options, type: 'info' });
};

const clearAll = () => {
    toastInstances.value.forEach(instance => {
        instance.app.unmount();
        instance.element.remove();
    });
    toastInstances.value = [];
};

export default {
    show,
    success,
    error,
    warning,
    info,
    clearAll
};
