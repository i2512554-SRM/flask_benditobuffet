(function(){
    const KEY = 'bendito_dark_mode';
    const root = document.documentElement;
    function apply(dark){
        // add class to root for existing CSS .dark-mode selectors
        if(dark) root.classList.add('dark-mode'); else root.classList.remove('dark-mode');
        // temporary transition class for smooth change
        root.classList.add('theme-transition');
        window.setTimeout(()=> root.classList.remove('theme-transition'), 250);
    }

    function getStored(){
        try { return localStorage.getItem(KEY); } catch(e) { return null; }
    }

    function setStored(val){
        try { localStorage.setItem(KEY, val); } catch(e) {}
    }

    // public toggle
    function toggle(){
        const active = root.classList.contains('dark-mode');
        apply(!active);
        setStored(!active ? '1' : '0');
    }

    // apply on load: priority -> stored preference -> system preference
    document.addEventListener('DOMContentLoaded', function(){
        const stored = getStored();
        if(stored === '1' || stored === '0'){
            apply(stored === '1');
        } else if(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches){
            apply(true);
        }

        // auto-bind buttons with data-theme-toggle attribute
        document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
            btn.addEventListener('click', function(e){
                e.preventDefault(); toggle();
            });
        });
    });

    // expose to window for manual calls
    window.benditoTheme = { toggle, apply };
})();
