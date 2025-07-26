import { useAuth } from '../contexts/AuthContext';
import { UserProfile } from '../components/UserProfile';

export const ProfilePage = () => {
  const { user, updateProfile } = useAuth();

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <p className="text-gray-500 dark:text-gray-400">Loading...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Profile & Settings
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Manage your account and study preferences
        </p>
      </div>
      
      <UserProfile user={user} onUpdateProfile={updateProfile} />
    </div>
  );
};
