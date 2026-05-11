<script>
    import Header from "./navbar.svelte";
    import Footer from "./footer.svelte";
    import "../app.css";
    import "$lib/style/footer.css";

    /** @type {{children: import('svelte').Snippet}} */
    let { children } = $props();
</script>

<div class="app">
    <Header />

    <main>
        {@render children()}
    </main>
    <link
        rel="stylesheet"
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    />

    <Footer />
</div>
