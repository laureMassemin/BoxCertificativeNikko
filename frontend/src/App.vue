<template>
  <div id="app">
    <nav style="margin-bottom: 20px; padding: 10px; background-color: #f0f0f0;">
      <router-link to="/trip" style="margin-right: 15px;">Voyage</router-link>
      <router-link to="/login">Connexion</router-link>
    </nav>

    <router-view />
  </div>
</template>

<style>
body {
  font-family: Arial, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
</style>