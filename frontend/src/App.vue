<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-gray-800 text-white py-3 px-6 flex items-center justify-between">
      <h1 class="font-semibold text-lg">CVForge</h1>
      <nav class="space-x-4">
        <RouterLink to="/">Dashboard</RouterLink>
        <RouterLink to="/profile">Profile</RouterLink>
        <RouterLink to="/projects">Projects</RouterLink>
        <RouterLink to="/experiences">Experiences</RouterLink>
        <RouterLink to="/generate">Generate</RouterLink>
      </nav>
    </header>

    <main class="flex-1 p-6">
      <RouterView />
    </main>

    <footer class="bg-gray-100 text-center py-2 text-sm text-gray-500">
      © 2025 CVForge
    </footer>
  </div>
</template>

<style scoped>
nav a {
  text-decoration: none;
  color: white;
  font-weight: 500;
}
nav a.router-link-exact-active {
  text-decoration: underline;
}
</style>
