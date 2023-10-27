
<template>
  <div>
    <file-upload/> <!-- Adicione o componente de upload aqui -->
  </div>
</template>

<script>
/* eslint-disable */
import FileUpload from "@/components/FileUpload.vue"; // Importe o componente de upload

export default {
  components: {
    FileUpload, // Registre o componente de upload
  },
};
</script>
