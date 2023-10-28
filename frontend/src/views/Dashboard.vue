<template>
  <div>
    <file-upload/> <!-- Add the file upload component here -->
  </div>
</template>

<script>
import FileUpload from "@/components/FileUpload.vue"; // Import the file upload component

export default {
  components: {
    FileUpload, // Register the file upload component
  },
};
</script>
