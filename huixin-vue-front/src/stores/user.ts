import { defineStore } from 'pinia';
import { ref } from 'vue';
import config from '@/config';

export const useUserStore = defineStore('user', () => {
  // Initialize user data from localStorage
  const initializeFromStorage = () => {
    const userInfoStr = localStorage.getItem('userInfo');
    if (userInfoStr) {
      try {
        const userInfo = JSON.parse(userInfoStr);
        return {
          id: userInfo.id || null,
          name: userInfo.name || '',
          email: userInfo.email || '',
          avatarUrl: userInfo.avatar ? `${config.baseURL}/uploads/avatars/${userInfo.avatar}` : ''
        };
      } catch (error) {
        console.error('Error parsing userInfo from localStorage:', error);
      }
    }
    return { id: null, name: '', email: '', avatarUrl: '' };
  };

  const initialData = initializeFromStorage();
  const id = ref(initialData.id);
  const name = ref(initialData.name);
  const email = ref(initialData.email);
  const avatarUrl = ref(initialData.avatarUrl);

  function setId(newId: string | null) {
    id.value = newId;
    // Update the userInfo in localStorage
    const userInfoStr = localStorage.getItem('userInfo');
    if (userInfoStr) {
      try {
        const userInfo = JSON.parse(userInfoStr);
        userInfo.id = newId;
        localStorage.setItem('userInfo', JSON.stringify(userInfo));
      } catch (error) {
        console.error('Error updating userInfo in localStorage:', error);
      }
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
