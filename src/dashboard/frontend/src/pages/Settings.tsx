import { useState } from 'react';
import { Save, Key, Database, Tv, Bell } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Card, CardHeader, Button } from '@/components/ui';
import toast from 'react-hot-toast';

export function Settings() {
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    removebg: '',
    elevenlabs: '',
  });

  const [notifications, setNotifications] = useState({
    emailOnComplete: true,
    emailOnError: true,
    slackIntegration: false,
  });

  const handleSaveApiKeys = () => {
    // Save to backend
    toast.success('API keys saved');
  };

  const handleSaveNotifications = () => {
    toast.success('Notification settings saved');
  };

  return (
    <Layout title="Settings" subtitle="Configure your Slasher TV AI system">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* API Keys */}
        <Card>
          <CardHeader 
            title="API Keys" 
            subtitle="Configure external service API keys"
            action={
              <div className="p-2 bg-amber-500/20 rounded-lg">
                <Key className="w-5 h-5 text-amber-400" />
              </div>
            }
          />
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">
                OpenAI API Key
              </label>
              <input
                type="password"
                className="input"
                placeholder="sk-..."
                value={apiKeys.openai}
                onChange={(e) => setApiKeys({ ...apiKeys, openai: e.target.value })}
              />
              <p className="text-xs text-dark-500 mt-1">Used for script generation</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">
                Remove.bg API Key
              </label>
              <input
                type="password"
                className="input"
                placeholder="..."
                value={apiKeys.removebg}
                onChange={(e) => setApiKeys({ ...apiKeys, removebg: e.target.value })}
              />
              <p className="text-xs text-dark-500 mt-1">Used for background removal</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">
                ElevenLabs API Key
              </label>
              <input
                type="password"
                className="input"
                placeholder="..."
                value={apiKeys.elevenlabs}
                onChange={(e) => setApiKeys({ ...apiKeys, elevenlabs: e.target.value })}
              />
              <p className="text-xs text-dark-500 mt-1">Used for premium voiceovers (optional)</p>
            </div>
            <Button onClick={handleSaveApiKeys} icon={<Save className="w-4 h-4" />}>
              Save API Keys
            </Button>
          </div>
        </Card>

        {/* Database */}
        <Card>
          <CardHeader 
            title="Database" 
            subtitle="MongoDB connection settings"
            action={
              <div className="p-2 bg-emerald-500/20 rounded-lg">
                <Database className="w-5 h-5 text-emerald-400" />
              </div>
            }
          />
          <div className="space-y-4">
            <div className="p-4 bg-dark-700/50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-dark-400">Status</span>
                <span className="flex items-center gap-2 text-emerald-400">
                  <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                  Connected
                </span>
              </div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-dark-400">Database</span>
                <span className="text-white font-mono">slasher-tv</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-dark-400">Collections</span>
                <span className="text-white">5</span>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">
                MongoDB URI
              </label>
              <input
                type="password"
                className="input"
                placeholder="mongodb://..."
                defaultValue="mongodb://localhost:27017/slasher-tv"
              />
            </div>
          </div>
        </Card>

        {/* FAST Channel */}
        <Card>
          <CardHeader 
            title="FAST Channel" 
            subtitle="Live playout configuration"
            action={
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <Tv className="w-5 h-5 text-purple-400" />
              </div>
            }
          />
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">
                Channel Name
              </label>
              <input
                type="text"
                className="input"
                placeholder="Slasher TV"
                defaultValue="Slasher TV"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-1">
                Playlist URL
              </label>
              <input
                type="text"
                className="input"
                placeholder="https://..."
              />
            </div>
            <div className="flex items-center justify-between p-4 bg-dark-700/50 rounded-lg">
              <div>
                <p className="font-medium text-white">Auto-publish to Channel</p>
                <p className="text-sm text-dark-400">Automatically add approved videos</p>
              </div>
              <button
                className="w-12 h-6 rounded-full bg-dark-600 transition-colors"
              >
                <div className="w-5 h-5 rounded-full bg-white shadow translate-x-0.5" />
              </button>
            </div>
          </div>
        </Card>

        {/* Notifications */}
        <Card>
          <CardHeader 
            title="Notifications" 
            subtitle="Configure alerts and notifications"
            action={
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Bell className="w-5 h-5 text-blue-400" />
              </div>
            }
          />
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-dark-700/50 rounded-lg">
              <div>
                <p className="font-medium text-white">Email on Completion</p>
                <p className="text-sm text-dark-400">Get notified when videos are ready</p>
              </div>
              <button
                onClick={() => setNotifications({ 
                  ...notifications, 
                  emailOnComplete: !notifications.emailOnComplete 
                })}
                className={`w-12 h-6 rounded-full transition-colors ${
                  notifications.emailOnComplete ? 'bg-primary-600' : 'bg-dark-600'
                }`}
              >
                <div className={`w-5 h-5 rounded-full bg-white shadow transition-transform ${
                  notifications.emailOnComplete ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
            <div className="flex items-center justify-between p-4 bg-dark-700/50 rounded-lg">
              <div>
                <p className="font-medium text-white">Email on Error</p>
                <p className="text-sm text-dark-400">Get notified when processing fails</p>
              </div>
              <button
                onClick={() => setNotifications({ 
                  ...notifications, 
                  emailOnError: !notifications.emailOnError 
                })}
                className={`w-12 h-6 rounded-full transition-colors ${
                  notifications.emailOnError ? 'bg-primary-600' : 'bg-dark-600'
                }`}
              >
                <div className={`w-5 h-5 rounded-full bg-white shadow transition-transform ${
                  notifications.emailOnError ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
            <div className="flex items-center justify-between p-4 bg-dark-700/50 rounded-lg">
              <div>
                <p className="font-medium text-white">Slack Integration</p>
                <p className="text-sm text-dark-400">Send notifications to Slack</p>
              </div>
              <button
                onClick={() => setNotifications({ 
                  ...notifications, 
                  slackIntegration: !notifications.slackIntegration 
                })}
                className={`w-12 h-6 rounded-full transition-colors ${
                  notifications.slackIntegration ? 'bg-primary-600' : 'bg-dark-600'
                }`}
              >
                <div className={`w-5 h-5 rounded-full bg-white shadow transition-transform ${
                  notifications.slackIntegration ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
            <Button onClick={handleSaveNotifications} icon={<Save className="w-4 h-4" />}>
              Save Notifications
            </Button>
          </div>
        </Card>
      </div>
    </Layout>
  );
}

