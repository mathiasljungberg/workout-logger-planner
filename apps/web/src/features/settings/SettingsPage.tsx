import { Page } from "../../components/Page";
import { Card } from "../../components/Card";

export function SettingsPage() {
  return (
    <Page title="Settings" description="Single-user configuration and deployment-oriented defaults.">
      <Card>
        <p>Authentication is deliberately minimal: one seeded admin account with a signed session cookie.</p>
        <p>Environment variables control database connection, secret key, and admin credentials.</p>
      </Card>
    </Page>
  );
}

