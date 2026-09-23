document.addEventListener('DOMContentLoaded', function() {
    const badge = document.getElementById('notificationBadge');
    const list = document.getElementById('notificationList');
    const dropdown = document.getElementById('notificationDropdown');
    
    if (!badge || !dropdown) return;

    function updateBadge() {
        fetch('/notificacoes/api/unread-count')
            .then(res => res.json())
            .then(data => {
                const count = data.unread_count;
                if (count > 0) {
                    badge.textContent = count > 99 ? '99+' : count;
                    badge.classList.remove('d-none');
                } else {
                    badge.classList.add('d-none');
                }
            })
            .catch(err => console.error('Erro ao carregar badge:', err));
    }

    function loadRecent() {
        fetch('/notificacoes/api/recent')
            .then(res => res.json())
            .then(data => {
                if (!list) return;
                
                if (data.notifications.length === 0) {
                    list.innerHTML = '<div class="p-3 text-center text-muted">Nenhuma notificação recente.</div>';
                    return;
                }
                
                let html = '';
                data.notifications.forEach(n => {
                    const isUnread = !n.read;
                    const bgClass = isUnread ? 'bg-light border-start border-primary border-3' : '';
                    
                    html += `
                        <a href="${n.link || '#'}" class="dropdown-item text-wrap p-2 border-bottom ${bgClass}" style="font-size: 0.85rem;">
                            <div class="d-flex justify-content-between">
                                <strong class="mb-1 ${isUnread ? 'text-primary' : 'text-dark'}">${n.title}</strong>
                            </div>
                            <div class="text-muted text-truncate" style="max-width: 280px;">${n.message}</div>
                        </a>
                    `;
                });
                
                list.innerHTML = html;
            })
            .catch(err => {
                console.error('Erro ao carregar notificações:', err);
                if (list) list.innerHTML = '<div class="p-3 text-center text-danger">Erro ao carregar notificações.</div>';
            });
    }

    // Inicializa contador
    updateBadge();
    
    // Atualiza a cada 60s
    setInterval(updateBadge, 60000);

    // Carrega a lista quando o dropdown for aberto
    dropdown.addEventListener('show.bs.dropdown', function () {
        loadRecent();
    });
});
