import { useEffect, useState } from "react";
import { Text, View } from "react-native";
import { getVersions } from "./services/api";

export default function App() {
  const [versions, setVersions] = useState<{python?: string; flask?: string; postgresql?: string}>({});

  useEffect(() => {
    getVersions().then(data => setVersions(data));
  }, []);

  return (
    <View style={{ padding: 40 }}>
      <Text>Python: {versions.python}</Text>
      <Text>Flask: {versions.flask}</Text>
      <Text>PostgreSQL: {versions.postgresql}</Text>
    </View>
  );
}