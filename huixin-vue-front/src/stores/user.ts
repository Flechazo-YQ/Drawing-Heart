import { defineStore } from 'pinia';
import { ref } from 'vue';
import config from '@/config';

export const useUserStore = defineStore('user', () => {
  const id = ref(localStorage.getItem('userId') || null);
  const name = ref('');
  const email = ref('');
  const avatarUrl = ref('');

  function setId(newId: string | null) {
    id.value = newId;
    if (newId) {
      localStorage.setItem('userId', newId);
    } else {
      localStorage.removeItem('userId');
    }
  }

  async function fetchUserInfo() {
    const token = localStorage.getItem('token');
    if (!token || !id.value) {
      console.error('No token or user ID found, cannot fetch user info.');
      return;
    }

    try {
      const response = await fetch(`${config.baseURL}/info`, {
        headers: {
          'Authorization': `${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user info');
      }

      const data = await response.json();
      name.value = data.name;
      email.value = data.email;
      // Assuming the backend returns a relative path for the avatar
      if (data.avatar) {
        avatarUrl.value = `${config.baseURL}/uploads/avatars/${data.avatar}`;
      }
    } catch (error) {
      console.error('Error fetching user info:', error);
      // Optionally clear user data on auth error
      // setId(null);
      // localStorage.removeItem('token');
    }
  }

  return { id, name, email, avatarUrl, setId, fetchUserInfo };
});
