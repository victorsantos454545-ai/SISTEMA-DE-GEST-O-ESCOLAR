/**
 * Sistema de Gestão Escolar - JavaScript Principal
 */

document.addEventListener('DOMContentLoaded', function () {

    // === Sidebar Toggle ===
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        // Criar overlay para mobile
        let overlay = document.querySelector('.sidebar-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);
        }

        sidebarToggle.addEventListener('click', function (e) {
            e.preventDefault();
            const isMobile = window.innerWidth < 992;

            if (isMobile) {
                sidebar.classList.toggle('show');
                overlay.classList.toggle('show');
            } else {
                sidebar.classList.toggle('toggled');
                const wrapper = document.getElementById('page-content-wrapper');
                if (wrapper) {
                    wrapper.style.marginLeft = sidebar.classList.contains('toggled') ? '0' : '';
                }
            }
        });

        // Fechar sidebar ao clicar no overlay
        overlay.addEventListener('click', function () {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });

        // Fechar sidebar ao redimensionar para desktop
        window.addEventListener('resize', function () {
            if (window.innerWidth >= 992) {
                sidebar.classList.remove('show');
                overlay.classList.remove('show');
            }
        });
    }

    // === Auto-dismiss de alertas ===
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // === Confirmação de exclusão ===
    document.addEventListener('click', function (e) {
        const deleteBtn = e.target.closest('[data-confirm]');
        if (deleteBtn) {
            const message = deleteBtn.getAttribute('data-confirm') || 'Tem certeza que deseja realizar esta ação?';
            if (!confirm(message)) {
                e.preventDefault();
                e.stopPropagation();
            }
        }
    });

    // === Tooltip Bootstrap ===
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    // === Máscara de CPF ===
    document.querySelectorAll('.mask-cpf').forEach(function (input) {
        input.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) value = value.substring(0, 11);
            if (value.length > 9) {
                value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, '$1.$2.$3-$4');
            } else if (value.length > 6) {
                value = value.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3');
            } else if (value.length > 3) {
                value = value.replace(/(\d{3})(\d{1,3})/, '$1.$2');
            }
            e.target.value = value;
        });
    });

    // === Máscara de telefone ===
    document.querySelectorAll('.mask-phone').forEach(function (input) {
        input.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) value = value.substring(0, 11);
            if (value.length > 10) {
                value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
            } else if (value.length > 6) {
                value = value.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
            } else if (value.length > 2) {
                value = value.replace(/(\d{2})(\d{0,5})/, '($1) $2');
            }
            e.target.value = value;
        });
    });

    // === Máscara de CEP ===
    document.querySelectorAll('.mask-cep').forEach(function (input) {
        input.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 8) value = value.substring(0, 8);
            if (value.length > 5) {
                value = value.replace(/(\d{5})(\d{1,3})/, '$1-$2');
            }
            e.target.value = value;
        });
    });

});
