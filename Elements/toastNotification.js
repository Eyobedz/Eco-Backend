class ToastNotification {
    constructor(containerSelector = 'body', defaultDuration = 5000) {
        this.container = document.createElement('div');
        this.container.className = 'notifications';
        document.querySelector(containerSelector).appendChild(this.container);
        this.defaultDuration = defaultDuration;
    }

    createToast(type, icon, title, text, duration = this.defaultDuration) {
        let newToast = document.createElement('div');
        newToast.className = `toast ${type}`;
        newToast.style.setProperty('--toast-duration', `${duration / 1000}s`); // Set duration dynamically
        
        newToast.innerHTML = `
            <i class="${icon}"></i>
            <div class="content">
                <div class="title">${title}</div>
                <span>${text}</span>
            </div>
            <i class="fa-solid fa-xmark close-btn"></i>
        `;

        this.container.appendChild(newToast);

        // Close button event
        newToast.querySelector('.close-btn').addEventListener('click', () => {
            newToast.remove();
        });

        // Auto remove toast
        setTimeout(() => newToast.remove(), duration);
    }

    success(text, duration) {
        this.createToast('success', 'fa-solid fa-circle-check', 'Success', text, duration);
    }
    error(text, duration) {
        this.createToast('error', 'fa-solid fa-circle-exclamation', 'Error', text, duration);
    }
    warning(text, duration) {
        this.createToast('warning', 'fa-solid fa-triangle-exclamation', 'Warning', text, duration);
    }
    info(text, duration) {
        this.createToast('info', 'fa-solid fa-circle-info', 'Info', text, duration);
    }
}
