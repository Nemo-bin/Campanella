import React from "react";
import {
  View,
  Text,
  StyleSheet,
  Image,
  ScrollView,
  TouchableOpacity
} from "react-native";

export default function HomeScreen() {
  const posts = [
    { id: 1, text: "First post from Expo 🚀" },
    { id: 2, text: "Building apps with React Native is fun." },
    { id: 3, text: "This is a sample home feed." }
  ];

  return (
    <ScrollView style={styles.container}>
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.logo}>MyApp</Text>
        <TouchableOpacity>
          <Text style={styles.profileButton}>Profile</Text>
        </TouchableOpacity>
      </View>

      {/* Profile Card */}
      <View style={styles.profileCard}>
        <Image
          source={{ uri: "https://i.pravatar.cc/150?img=12" }}
          style={styles.avatar}
        />

        <Text style={styles.name}>Ben</Text>
        <Text style={styles.bio}>Computer Science student 🚀</Text>

        <View style={styles.statsRow}>
          <View style={styles.stat}>
            <Text style={styles.statNumber}>120</Text>
            <Text style={styles.statLabel}>Posts</Text>
          </View>

          <View style={styles.stat}>
            <Text style={styles.statNumber}>2.4k</Text>
            <Text style={styles.statLabel}>Followers</Text>
          </View>

          <View style={styles.stat}>
            <Text style={styles.statNumber}>180</Text>
            <Text style={styles.statLabel}>Following</Text>
          </View>
        </View>
      </View>

      {/* Feed */}
      <View style={styles.feed}>
        <Text style={styles.sectionTitle}>Latest Posts</Text>

        {posts.map(post => (
          <View key={post.id} style={styles.postCard}>
            <Text style={styles.postText}>{post.text}</Text>
          </View>
        ))}
      </View>

    </ScrollView>
  );
}

const styles = StyleSheet.create({

  container: {
    flex: 1,
    backgroundColor: "#EEE9DF"
  },

  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 20,
    paddingTop: 60
  },

  logo: {
    fontSize: 28,
    fontWeight: "bold"
  },

  profileButton: {
    fontSize: 16,
    color: "#444"
  },

  profileCard: {
    alignItems: "center",
    backgroundColor: "white",
    margin: 20,
    padding: 20,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 10
  },

  avatar: {
    width: 90,
    height: 90,
    borderRadius: 45,
    marginBottom: 10
  },

  name: {
    fontSize: 22,
    fontWeight: "bold"
  },

  bio: {
    color: "#666",
    marginBottom: 15
  },

  statsRow: {
    flexDirection: "row",
    gap: 30
  },

  stat: {
    alignItems: "center"
  },

  statNumber: {
    fontSize: 18,
    fontWeight: "bold"
  },

  statLabel: {
    color: "#666"
  },

  feed: {
    paddingHorizontal: 20
  },

  sectionTitle: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 10
  },

  postCard: {
    backgroundColor: "white",
    padding: 15,
    borderRadius: 10,
    marginBottom: 12
  },

  postText: {
    fontSize: 16
  }

});