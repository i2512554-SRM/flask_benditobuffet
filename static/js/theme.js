(function(){
    const KEY = 'dark-mode';
    const root = document.documentElement;
    const body = document.body;

    function setRootClass(dark) {
        if (dark) {
            root.classList.add('dark-mode');
            if (document.body) document.body.classList.add('dark-mode');
        } else {
            root.classList.remove('dark-mode');
            if (document.body) document.body.classList.remove('dark-mode');
        }
    }

    function apply(dark){
        setRootClass(dark);
        // temporary transition class for smooth change
        root.classList.add('theme-transition');
        window.setTimeout(()=> root.classList.remove('theme-transition'), 250);
        updateToggleButtons(dark);
    }

    function getStored(){
        try { return localStorage.getItem(KEY); } catch(e) { return null; }
    }

    function setStored(val){
        try { localStorage.setItem(KEY, val); } catch(e) {}
    }

    function updateToggleButtons(active) {
        document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
            btn.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
    }

    // public toggle
    function toggle(){
        const active = root.classList.contains('dark-mode') || document.body.classList.contains('dark-mode');
        const next = !active;
        apply(next);
        setStored(next ? 'true' : 'false');
    }

    // apply on load: priority -> stored preference -> system preference
    document.addEventListener('DOMContentLoaded', function(){
        const stored = getStored();
        if(stored === 'true' || stored === 'false'){
            apply(stored === 'true');
        } else if(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches){
            apply(true);
            setStored('true');
        } else {
            updateToggleButtons(false);
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
